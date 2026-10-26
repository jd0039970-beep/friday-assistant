"""FastAPI entrypoint for F.R.I.D.A.Y."""
from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .core.agent_loop import AgentConfig, AgentLoop
from .core.llm_client import OllamaClient
from .memory.store import MemoryStore
from .proactive import ProactiveMonitor
from .sandbox.audit_log import AuditLog
from .sandbox.controller import SandboxController
from .sandbox.security_tools import register_security_tools, workshop
from .skills.packs.forensics import list_forensics_packs
from .skills.store import list_skills, create_skill, run_skill, promote_skill
from .tools.input_tools import register_input_tools
from .tools.registry import ToolRegistry
from .tools.shell_tools import register_shell_tools
from .tools.system_tools import register_system_tools
from .tools.web_tools import register_web_tools
from .vision.screen import screen_text, capture_screenshot
from .vision.webcam import capture_webcam

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


config = load_config()
app = FastAPI(title="F.R.I.D.A.Y", version="0.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HUD_DIR = Path(__file__).resolve().parents[2] / "frontend" / "hud"
if HUD_DIR.exists():
    app.mount("/hud", StaticFiles(directory=str(HUD_DIR), html=True), name="hud")

llm = OllamaClient(base_url=config["llm"]["base_url"], model=config["llm"]["model"],
                   temperature=config["llm"].get("temperature", 0.4))
memory = MemoryStore(config["memory"]["db_path"])
audit_log = AuditLog(config["audit_log_path"])
sandbox = SandboxController(config["sandbox"], audit_log)
proactive = ProactiveMonitor(interval=15.0)

tools = ToolRegistry()
register_system_tools(tools)
register_input_tools(tools)
register_shell_tools(tools)
register_security_tools(tools, sandbox, voice_sourced=False)
register_web_tools(tools, headless=config.get("web", {}).get("headless", True))

tools.register("what_is_on_screen", "Screenshot + OCR",
               {"type": "object", "properties": {}}, lambda: screen_text())
tools.register("take_screenshot", "Save screenshot",
               {"type": "object", "properties": {}}, lambda: capture_screenshot())
tools.register("capture_webcam", "Webcam frame",
               {"type": "object", "properties": {}}, lambda: capture_webcam())
tools.register("list_skills", "List custom skills",
               {"type": "object", "properties": {}}, list_skills)
tools.register("create_skill", "Draft new skill",
               {"type": "object", "properties": {
                   "name": {"type": "string"}, "description": {"type": "string"}, "code": {"type": "string"},
               }, "required": ["name", "description", "code"]}, create_skill)
tools.register("run_skill", "Run custom skill",
               {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}, run_skill)
tools.register("promote_skill", "Promote skill",
               {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}, promote_skill)
tools.register("list_forensics_packs", "List built-in forensics workflows",
               {"type": "object", "properties": {}}, list_forensics_packs)

tools.workshop_relaxed = workshop.enabled

agent = AgentLoop(llm, tools, memory, AgentConfig(
    max_tool_iterations=config["llm"].get("max_tool_iterations", 10),
    embed_model=config["llm"]["embed_model"],
    recall_k=config["memory"].get("recall_k", 8),
), on_tool_call=lambda n, a, r: audit_log.write("tool_call", tool=n, arguments=a, result_preview=str(r)[:300]))

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
    tool_trace: list | None = None
    eta_seconds: int | None = None
    workshop_mode: bool = False


@app.on_event("startup")
def _start_proactive():
    proactive.start()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    tools.workshop_relaxed = workshop.enabled
    history = _sessions.setdefault(req.session_id, [])
    pending = (req.confirm_tool, req.confirm_arguments) if req.confirm_tool else None
    result = agent.run(req.message, history=history, pending_confirmation=pending)
    if result["needs_confirmation"] is None and result.get("reply"):
        history.append({"role": "user", "content": req.message})
        history.append({"role": "assistant", "content": result["reply"]})
        try:
            emb = llm.embed(req.message, config["llm"]["embed_model"])
            memory.add(f"User: {req.message}\nFriday: {result['reply']}", embedding=emb)
        except Exception:
            pass
    return ChatResponse(
        reply=result["reply"],
        needs_confirmation=result["needs_confirmation"],
        sandbox_state=sandbox.current_state(),
        tool_trace=result.get("tool_trace"),
        eta_seconds=result.get("eta_seconds"),
        workshop_mode=workshop.enabled,
    )


@app.get("/proactive")
def get_proactive():
    return {"suggestions": proactive.pop_suggestions()}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": config["llm"]["model"],
        "sandbox_state": sandbox.current_state(),
        "workshop_mode": workshop.enabled,
        "trusted_targets": len(workshop.trusted),
        "version": "0.5.0",
    }


@app.get("/tools")
def list_tools():
    return [s["function"]["name"] for s in tools.schemas()]


@app.get("/audit")
def get_audit(n: int = 50):
    return audit_log.tail(n)


if __name__ == "__main__":
    import uvicorn
    print("F.R.I.D.A.Y online")
    print("  API  → http://127.0.0.1:8787")
    print("  HUD  → http://127.0.0.1:8787/hud/")
    print("  Tab = push-to-talk · Esc = silence")
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])
