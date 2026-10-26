"""Security + forensics tools Friday can drive herself."""
from __future__ import annotations

from ..tools.registry import ToolRegistry
from .controller import SandboxController
from .workshop import WorkshopState

workshop = WorkshopState()


def register_security_tools(reg: ToolRegistry, sandbox: SandboxController, voice_sourced: bool = False):
    def _guard_voice(action: str) -> str | None:
        if voice_sourced:
            return f"REFUSED: {action} must be typed."
        return None

    def request_go_live(target: str, owner_attestation: bool = False) -> str:
        if (msg := _guard_voice("Go-Live")):
            return msg
        if workshop.is_trusted(target):
            sandbox.request_go_live(target, owner_attestation=True)
            if sandbox._pending:
                return sandbox.confirm_go_live(target, sandbox._pending.token)
        return sandbox.request_go_live(target, owner_attestation)

    def confirm_go_live(target: str, token: str) -> str:
        if (msg := _guard_voice("confirm")):
            return msg
        return sandbox.confirm_go_live(target, token)

    def stand_down() -> str:
        return sandbox.stand_down()

    def run_nmap(target: str, flags: str = "-sV") -> str:
        return sandbox.run_security_tool("nmap", flags.split() + [target], target)

    def run_hashcat(hash_file: str, wordlist: str, mode: str = "0") -> str:
        """mode 0 = MD5, 1000 = NTLM, 1800 = sha512crypt, etc."""
        args = ["-m", mode, hash_file, wordlist, "--force"]
        return sandbox.run_security_tool("hashcat", args, hash_file)

    def run_john(hash_file: str, wordlist: str | None = None) -> str:
        args = [hash_file]
        if wordlist:
            args += ["--wordlist=" + wordlist]
        return sandbox.run_security_tool("john", args, hash_file)

    def run_binwalk(path: str, extract: bool = False) -> str:
        args = [path]
        if extract:
            args.insert(0, "-e")
        return sandbox.run_security_tool("binwalk", args, path)

    def run_file(path: str) -> str:
        return sandbox.run_security_tool("file", [path], path)

    def run_strings(path: str, min_len: int = 8) -> str:
        return sandbox.run_security_tool("strings", ["-n", str(min_len), path], path)

    def enable_workshop_mode() -> str:
        if (msg := _guard_voice("Workshop Mode")):
            return msg
        return workshop.enable()

    def add_trusted_target(target: str) -> str:
        if (msg := _guard_voice("trusted target")):
            return msg
        return workshop.add_trusted(target)

    def list_trusted() -> str:
        if not workshop.trusted:
            return "No trusted targets."
        return "Trusted:\n" + "\n".join(f"- {t}" for t in workshop.trusted)

    # Register
    reg.register("request_go_live", "Take a target Live (lab/forensics)",
                 {"type": "object", "properties": {"target": {"type": "string"}, "owner_attestation": {"type": "boolean"}}, "required": ["target"]}, request_go_live)
    reg.register("confirm_go_live", "Confirm Live with token",
                 {"type": "object", "properties": {"target": {"type": "string"}, "token": {"type": "string"}}, "required": ["target", "token"]}, confirm_go_live)
    reg.register("stand_down", "Return to sandbox",
                 {"type": "object", "properties": {}}, stand_down)
    reg.register("run_nmap", "Port/service scan",
                 {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string"}}, "required": ["target"]}, run_nmap)
    reg.register("run_hashcat", "Crack hashes with hashcat",
                 {"type": "object", "properties": {"hash_file": {"type": "string"}, "wordlist": {"type": "string"}, "mode": {"type": "string"}}, "required": ["hash_file", "wordlist"]}, run_hashcat)
    reg.register("run_john", "Crack hashes with John the Ripper",
                 {"type": "object", "properties": {"hash_file": {"type": "string"}, "wordlist": {"type": "string"}}, "required": ["hash_file"]}, run_john)
    reg.register("run_binwalk", "Firmware / image analysis",
                 {"type": "object", "properties": {"path": {"type": "string"}, "extract": {"type": "boolean"}}, "required": ["path"]}, run_binwalk)
    reg.register("run_file", "Identify file type",
                 {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, run_file)
    reg.register("run_strings", "Extract readable strings from binary",
                 {"type": "object", "properties": {"path": {"type": "string"}, "min_len": {"type": "integer"}}, "required": ["path"]}, run_strings)
    reg.register("enable_workshop_mode", "Enable Workshop Mode (typed)",
                 {"type": "object", "properties": {}}, enable_workshop_mode)
    reg.register("add_trusted_target", "Trust a lab target",
                 {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}, add_trusted_target)
    reg.register("list_trusted", "Show trusted targets",
                 {"type": "object", "properties": {}}, list_trusted)
