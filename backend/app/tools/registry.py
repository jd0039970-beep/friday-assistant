"""Tool registry with JSON schemas and dispatch."""
from __future__ import annotations

from typing import Any, Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, name: str, description: str, parameters: dict, handler: Callable, requires_confirmation: bool = False):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
            "requires_confirmation": requires_confirmation,
        }

    def schemas(self) -> list[dict]:
        out = []
        for t in self._tools.values():
            out.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            })
        return out

    def call(self, name: str, arguments: dict) -> Any:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]["handler"](**arguments)

    def requires_confirmation(self, name: str) -> bool:
        return self._tools.get(name, {}).get("requires_confirmation", False)
