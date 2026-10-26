"""Security + Workshop Mode tools."""
from __future__ import annotations

from ..tools.registry import ToolRegistry
from .controller import SandboxController
from .workshop import WorkshopState

workshop = WorkshopState()


def register_security_tools(reg: ToolRegistry, sandbox: SandboxController, voice_sourced: bool = False):
    def request_go_live(target: str, owner_attestation: bool = False) -> str:
        if voice_sourced:
            return "REFUSED: Go-Live must be typed."
        # Trusted lab target under Workshop Mode → auto-grant short live window
        if workshop.is_trusted(target):
            sandbox.request_go_live(target, owner_attestation=True)
            # auto-confirm with the pending token
            if sandbox._pending:
                return sandbox.confirm_go_live(target, sandbox._pending.token)
            return sandbox.request_go_live(target, True)
        return sandbox.request_go_live(target, owner_attestation)

    def confirm_go_live(target: str, token: str) -> str:
        if voice_sourced:
            return "REFUSED: confirmation must be typed."
        return sandbox.confirm_go_live(target, token)

    def stand_down() -> str:
        return sandbox.stand_down()

    def run_nmap(target: str, flags: str = "-sV") -> str:
        args = flags.split() + [target]
        return sandbox.run_security_tool("nmap", args, target)

    def enable_workshop_mode() -> str:
        if voice_sourced:
            return "REFUSED: Workshop Mode must be enabled by typed command."
        return workshop.enable()

    def add_trusted_target(target: str) -> str:
        if voice_sourced:
            return "REFUSED: typed only."
        return workshop.add_trusted(target)

    reg.register("request_go_live", "Request live mode for a target",
                 {"type": "object", "properties": {"target": {"type": "string"}, "owner_attestation": {"type": "boolean"}}, "required": ["target"]}, request_go_live)
    reg.register("confirm_go_live", "Confirm Go-Live with token",
                 {"type": "object", "properties": {"target": {"type": "string"}, "token": {"type": "string"}}, "required": ["target", "token"]}, confirm_go_live)
    reg.register("stand_down", "Return to sandbox",
                 {"type": "object", "properties": {}}, stand_down)
    reg.register("run_nmap", "Run nmap (sandbox or live if granted/trusted)",
                 {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string"}}, "required": ["target"]}, run_nmap)
    reg.register("enable_workshop_mode", "Enable Workshop Mode (typed once). Trusted targets then auto-live.",
                 {"type": "object", "properties": {}}, enable_workshop_mode)
    reg.register("add_trusted_target", "Add a lab target to the trusted list",
                 {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}, add_trusted_target)
