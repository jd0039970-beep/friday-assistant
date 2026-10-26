"""FastAPI entrypoint for F.R.I.D.A.Y."""
from __future__ import annotations

import os
import signal
import threading
from pathlib import Path

import yaml
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .bootcheck import run_boot_check
from .core.agent_loop import AgentConfig, AgentLoop
from .core.llm_client import OllamaClient
from .core.planner import create_plan, list_plans, plan_status, mark_step
from .memory.store import MemoryStore
from .proactive import ProactiveMonitor
from .sandbox.audit_log import AuditLog
from .sandbox.controller import SandboxController
from .sandbox.security_tools import register_security_tools, workshop
from .skills.packs.forensics import list_forensics_packs, run_forensics_pack
from .skills.store import list_skills, create_skill, run_skill, promote_skill
from .tools.input_tools import register_input_tools
from .tools.registry import ToolRegistry
from .tools.shell_tools import register_shell_tools
from .tools.system_tools import register_system_tools
from .tools.web_tools import register_web_tools
from .vision.screen import screen_text, capture_screenshot
from .vision.webcam import capture_webcam
from .voice.stt import FasterWhisperSTT

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


config = load_config()
app = FastAPI(title="F.R.I.D.A.Y", version="0.7.0")
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
stt = FasterWhisperSTT(model_size=config.get("voice", {}).get("stt_model", "small.en").replace("faster-whisper ", ""))

LAST_BOOT: dict | None = None

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
tools.register("list_forensics_packs", "List forensics packs",
               {"type": "object", "properties": {}}, list_forensics_packs)


def _run_pack(pack: str, target: str, hash_file: str | None = None, wordlist: str | None = None) -> str:
    return run_forensics_pack(
        pack, target,
        run_file=lambda p: sandbox.run_security_tool("file", [p], p),
        run_strings=lambda p, min_len=8: sandbox.run_security_tool("strings", ["-n", str(min_len), p], p),
        run_binwalk=lambda p, extract=False: sandbox.run_security_tool(
            "binwalk", (["-e", p] if extract else [p]), p),
        run_hashcat=lambda hf, wl, mode="0": sandbox.run_security_tool(
            "hashcat", ["-m", mode, hf, wl, "--force"], hf),
        hash_file=hash_file, wordlist=wordlist,
    )


tools.register(
    "run_forensics_pack",
    "Run forensics pack on target",
    {"type": "object", "properties": {
        "pack": {"type": "string"}, "target": {"type": "string"},
        "hash_file": {"type": "string"}, "wordlist": {"type": "string"},
    }, "required": ["pack", "target"]},
    _run_pack,
)

# Long-task planner tools
tools.register(
    "create_plan",
    "Create a multi-step plan for a long goal. Pass goal + list of step descriptions.",
    {"type": "object", "properties": {
        "goal": {"type": "string"},
        "steps": {"type": "array", "items": {"type": "string"}},
    }, "required": ["goal", "steps"]},
    lambda goal, steps: (
        lambda p: f"Plan {p.id} created for: {goal}\n" + "\n".join(f"  {s.id}. {s.description}" for s in p.steps)
    )(create_plan(goal, steps)),
)
tools.register("list_plans", "List saved long-task plans",
               {"type": "object", "properties": {}}, list_plans)
tools.register("plan_status", "Show plan progress",
               {"type": "object", "properties": {"plan_id": {"type": "string"}}, "required": ["plan_id"]}, plan_status)
tools.register(
    "mark_step",
    "Update a plan step status (pending|running|done|failed|skipped) and optional result text",
    {"type": "object", "properties": {
        "plan_id": {"type": "string"}, "step_id": {"type": "string"},
        "status": {"type": "string"}, "result": {"type": "string"},
    }, "required": ["plan_id", "step_id", "status"]},
    mark_step,
)

tools.workshop_relaxed = workshop.enabled

agent = AgentLoop(llm, tools, memory, AgentConfig(
    max_tool_iterations=config["llm"].get("max_tool_iterations", 12),
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
    transcript: str | None = None


def _do_boot() -> str:
    global LAST_BOOT
    smoke = {
        "system_info": lambda: tools.call("system_info", {}),
        "list_dir_home": lambda: tools.call("list_dir", {"path": "~"}),
        "list_forensics": list_forensics_packs,
        "list_skills": list_skills,
        "list_plans": list_plans,
    }
    report = run_boot_check(ollama_url=config["llm"]["base_url"], test_tools=smoke)
    LAST_BOOT = {"all_ok": report.all_ok, "summary": report.summary(),
                 "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in report.checks]}
    audit_log.write("boot_check", all_ok=report.all_ok, n=len(report.checks))
    return report.summary()


@app.on_event("startup")
def _startup():
    proactive.start()
    summary = _do_boot()
    print(summary)


def _run_chat(message: str, session_id: str = "default") -> ChatResponse:
    tools.workshop_relaxed = workshop.enabled
    history = _sessions.setdefault(session_id, [])
    result = agent.run(message, history=history, pending_confirmation=None)
    if result["needs_confirmation"] is None and result.get("reply"):
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": result["reply"]})
        try:
            emb = llm.embed(message, config["llm"]["embed_model"])
            memory.add(f"User: {message}\nFriday: {result['reply']}", embedding=emb)
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


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return _run_chat(req.message, req.session_id)


@app.post("/voice", response_model=ChatResponse)
async def voice(file: UploadFile = File(...), session_id: str = "default"):
    data = await file.read()
    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    try:
        text = stt.transcribe_bytes(data, suffix=suffix)
    except Exception as e:
        return ChatResponse(reply=f"I couldn't hear that clearly ({e}).",
                            needs_confirmation=None, sandbox_state=sandbox.current_state(),
                            workshop_mode=workshop.enabled, transcript="")
    if not text.strip():
        return ChatResponse(reply="I didn't catch anything. Hold Tab and speak again.",
                            needs_confirmation=None, sandbox_state=sandbox.current_state(),
                            workshop_mode=workshop.enabled, transcript="")
    resp = _run_chat(text, session_id)
    resp.transcript = text
    return resp


@app.get("/bootcheck")
def bootcheck(refresh: bool = False):
    if refresh or LAST_BOOT is None:
        _do_boot()
    return LAST_BOOT


@app.post("/shutdown")
def shutdown():
    try:
        sandbox.stand_down()
    except Exception:
        pass
    try:
        proactive.stop()
    except Exception:
        pass
    audit_log.write("shutdown", reason="user Esc / API")

    def _exit():
        import time
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=_exit, daemon=True).start()
    return {"status": "shutting_down"}


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
        "boot_ok": None if LAST_BOOT is None else LAST_BOOT.get("all_ok"),
        "version": "0.7.0",
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
    print("  Tab = talk · Esc = SHUT DOWN")
    uvicorn.run(app, host=config["server"]["host"], port=config["server"]["port"])
