"""The ReAct-style agent loop."""
from __future__ import annotations

from dataclasses import dataclass

from ..memory.store import MemoryStore
from ..tools.registry import ToolRegistry
from .llm_client import OllamaClient
from .persona import build_system_prompt


@dataclass
class AgentConfig:
    max_tool_iterations: int = 8
    embed_model: str = "nomic-embed-text"
    recall_k: int = 6


class AgentLoop:
    def __init__(self, llm: OllamaClient, tools: ToolRegistry, memory: MemoryStore, config: AgentConfig, on_tool_call=None):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.config = config
        self.on_tool_call = on_tool_call

    def _recall(self, query: str) -> list[str]:
        try:
            emb = self.llm.embed(query, self.config.embed_model)
            return self.memory.search(emb, k=self.config.recall_k)
        except Exception:
            return []

    def run(self, user_message: str, history: list[dict] | None = None, pending_confirmation: tuple | None = None) -> dict:
        history = history or []
        memories = self._recall(user_message)
        system_prompt = build_system_prompt(memories)

        messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}]
        tool_trace = []

        # handle pending confirmation first
        if pending_confirmation:
            name, args = pending_confirmation
            try:
                result = self.tools.call(name, args)
                tool_trace.append({"tool": name, "args": args, "result": str(result)[:500]})
                if self.on_tool_call:
                    self.on_tool_call(name, args, result)
                messages.append({"role": "assistant", "content": None, "tool_calls": [{"id": "conf1", "function": {"name": name, "arguments": args}}]})
                messages.append({"role": "tool", "content": str(result), "tool_call_id": "conf1"})
            except Exception as e:
                return {"reply": f"Tool failed after confirmation: {e}", "tool_trace": tool_trace, "needs_confirmation": None}

        for _ in range(self.config.max_tool_iterations):
            response = self.llm.chat(messages, tools=self.tools.schemas())

            if not response.tool_calls:
                return {"reply": response.content or "", "tool_trace": tool_trace, "needs_confirmation": None}

            for tc in response.tool_calls:
                # check if tool requires confirmation
                if self.tools.requires_confirmation(tc.name):
                    return {
                        "reply": f"I need your confirmation before running `{tc.name}` with {tc.arguments}.", 
                        "tool_trace": tool_trace,
                        "needs_confirmation": {"tool": tc.name, "arguments": tc.arguments},
                    }

                try:
                    result = self.tools.call(tc.name, tc.arguments)
                except Exception as e:
                    result = f"ERROR: {e}"

                tool_trace.append({"tool": tc.name, "args": tc.arguments, "result": str(result)[:500]})
                if self.on_tool_call:
                    self.on_tool_call(tc.name, tc.arguments, result)

                messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [{"id": tc.id, "function": {"name": tc.name, "arguments": tc.arguments}}],
                })
                messages.append({"role": "tool", "content": str(result), "tool_call_id": tc.id})

        return {"reply": "I hit the tool iteration limit. Please try a simpler request.", "tool_trace": tool_trace, "needs_confirmation": None}
