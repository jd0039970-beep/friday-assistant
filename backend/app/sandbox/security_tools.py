"""Security tool orchestration (nmap, hashcat, etc.)."""
from __future__ import annotations

from ..tools.registry import ToolRegistry
from .controller import SandboxController


def register_security_tools(reg: ToolRegistry, sandbox: SandboxController, voice_sourced: bool = False):
    def request_go_live(target: str, owner_attestation: bool = False) -> str:
        if voice_sourced:
            return "REFUSED: Go-Live cannot be triggered by voice. Type the command."
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

    reg.register("request_go_live", "Request live mode for a specific target (typed confirmation required)",
                 {"type": "object", "properties": {"target": {"type": "string"}, "owner_attestation": {"type": "boolean"}}, "required": ["target"]}, request_go_live)
    reg.register("confirm_go_live", "Confirm a pending Go-Live with the one-time token",
                 {"type": "object", "properties": {"target": {"type": "string"}, "token": {"type": "string"}}, "required": ["target", "token"]}, confirm_go_live)
    reg.register("stand_down", "Revoke live mode and return to sandbox",
                 {"type": "object", "properties": {}}, stand_down)
    reg.register("run_nmap", "Run nmap (sandbox by default, live only if granted for that target)",
                 {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string"}}, "required": ["target"]}, run_nmap)
