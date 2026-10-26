"""ReAct-style agent loop with tool routing and ETA hints."""
from __future__ import annotations

from dataclasses import dataclass
from time import time

from ..memory.store import MemoryStore
from ..tools.registry import ToolRegistry
from .llm_client import OllamaClient
from .persona import build_system_prompt
from .tool_router import select_tools


@dataclass
class AgentConfig:
    max_tool_iterations: int = 10
    embed_model: str = "nomic-embed-text"
    recall_k: int = 8


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
        t0 = time()
        history = history or []
        memories = self._recall(user_message)
        system_prompt = build_system_prompt(memories)

        messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}]
        tool_trace = []
        all_schemas = self.tools.schemas()
        # Only send relevant tools this turn
        active_schemas = select_tools(user_message, all_schemas)

        if pending_confirmation:
            name, args = pending_confirmation
            try:
                result = self.tools.call(name, args)
                tool_trace.append({"tool": name, "args": args, "result": str(result)[:1200]})
                if self.on_tool_call:
                    self.on_tool_call(name, args, result)
                messages.append({"role": "tool", "content": str(result)})
            except Exception as e:
                return {"reply": f"Tool failed: {e}", "tool_trace": tool_trace, "needs_confirmation": None, "eta_seconds": 0}

        for i in range(self.config.max_tool_iterations):
            response = self.llm.chat(messages, tools=active_schemas)

            if not response.tool_calls:
                elapsed = time() - t0
                return {
                    "reply": response.content or "",
                    "tool_trace": tool_trace,
                    "needs_confirmation": None,
                    "eta_seconds": max(0, int(8 - elapsed)),
                }

            for tc in response.tool_calls:
                # In Workshop Mode most tools auto-run; only truly dangerous ones still flag
                if self.tools.requires_confirmation(tc.name) and not getattr(self.tools, "workshop_relaxed", False):
                    return {
                        "reply": f"Confirm `{tc.name}` with args {tc.arguments}?\n(Workshop Mode reduces these prompts for trusted lab work.)",
                        "tool_trace": tool_trace,
                        "needs_confirmation": {"tool": tc.name, "arguments": tc.arguments},
                        "eta_seconds": 0,
                    }

                try:
                    result = self.tools.call(tc.name, tc.arguments)
                except Exception as e:
                    result = f"ERROR: {e}"

                tool_trace.append({"tool": tc.name, "args": tc.arguments, "result": str(result)[:1200]})
                if self.on_tool_call:
                    self.on_tool_call(tc.name, tc.arguments, result)

                messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [{"id": tc.id, "function": {"name": tc.name, "arguments": tc.arguments}}],
                })
                messages.append({"role": "tool", "content": str(result), "tool_call_id": tc.id})

        return {
            "reply": "Hit the tool iteration limit. Try a narrower request.",
            "tool_trace": tool_trace,
            "needs_confirmation": None,
            "eta_seconds": 0,
        }
