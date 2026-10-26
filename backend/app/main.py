"""FastAPI entrypoint. Run with: python -m app.main (from backend/)."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from fastapi import FastAPI
from pydantic import BaseModel

from .core.agent_loop import AgentConfig, AgentLoop
from .core.llm_client import OllamaClient
from .memory.store import MemoryStore
from .sandbox.audit_log import AuditLog
from .sandbox.controller import SandboxController
from .sandbox.security_tools import register_security_tools
from .tools.input_tools import register_input_tools
from .tools.registry import ToolRegistry
from .tools.system_tools import register_system_tools

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


config = load_config()
app = FastAPI(title="F.R.I.D.A.Y backend")

llm = OllamaClient(
    base_url=config["llm"]["base_url"],
    model=config["llm"]["model"],
    temperature=config["llm"].get("temperature", 0.4),
)
memory = MemoryStore(config["memory"]["db_path"])
audit_log = AuditLog(config["audit_log_path"])
sandbox = SandboxController(config["sandbox"], audit_log)

tools = ToolRegistry()
register_system_tools(tools)
register_input_tools(tools)
register_security_tools(tools, sandbox, voice_sourced=False)

agent_config = AgentConfig(
    max_tool_iterations=config["llm"].get("max_tool_iterations", 8),
    embed_model=config["llm"]["embed_model"],
    recall_k=config["memory"].get("recall_k", 6),
)


def log_tool_call(name, args, result):
    audit_log.write("tool_call", tool=name, arguments=args, result_preview=str(result)[:300])


agent = AgentLoop(llm, tools, memory, agent_config, on_tool_call=log_tool_call)

_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str
    confirm_tool: str | None = None
    confirm_arguments: dict | None = None


class ChatResponse(BaseModel):
    reply: str | None
    needs_confirmation: dict | None
    sandbox_state: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = _sessions.setdefault(req.session_id, [])
    pending = (req.confirm_tool, req.confirm_arguments) if req.confirm_tool else None

    result = agent.run(req.message, history=history, pending_confirmation=pending)

    if result["needs_confirmation"] is None:
        history.append({"role": "user", "content": req.message})
        history.append({"role": "assistant", "content": result["reply"]})
        # memory write is best-effort
        try:
            agent.memory.add(f"User: {req.message}\nFriday: {result['reply']}")
        except Exception:
            pass

    return ChatResponse(
        reply=result["reply"],
        needs_confirmation=result["needs_confirmation"],
        sandbox_state=sandbox.current_state(),
    )


@app.get("/audit")
def get_audit(n: int = 50):
    return audit_log.tail(n)


@app.get("/health")
def health():
    return {"status": "ok", "model": config["llm"]["model"], "sandbox_state": sandbox.current_state()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])
