"""Thin client around a local Ollama server, using its OpenAI-compatible tool-calling chat endpoint."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import httpx


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: dict | None = None


class OllamaClient:
    def __init__(self, base_url: str, model: str, temperature: float = 0.4):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self._client = httpx.Client(timeout=120.0)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if tools:
            payload["tools"] = tools

        resp = self._client.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        msg = data.get("message", {})
        tool_calls = []
        for i, tc in enumerate(msg.get("tool_calls", []) or []):
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            tool_calls.append(ToolCall(id=str(tc.get("id", i)), name=fn.get("name", ""), arguments=args))

        return LLMResponse(content=msg.get("content"), tool_calls=tool_calls, raw=data)

    def embed(self, text: str, embed_model: str) -> list[float]:
        resp = self._client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": embed_model, "prompt": text},
        )
        resp.raise_for_status()
        return resp.json().get("embedding", [])
