"""Sandbox / Go-Live state machine. See SAFETY.md."""
from __future__ import annotations

import datetime
import ipaddress
import re
import subprocess
import uuid
from dataclasses import dataclass

from .audit_log import AuditLog

PRIVATE_NETS = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
)]
ALLOWED_SANDBOX_CMDS = {"nmap", "hashcat", "john", "binwalk", "strings", "file"}


def _looks_like_private_target(target: str) -> bool:
    host = target.split("/")[0]
    try:
        return any(ipaddress.ip_address(host) in net for net in PRIVATE_NETS)
    except ValueError:
        return host.endswith(".local") or host in ("localhost",)


@dataclass
class PendingConfirmation:
    target: str
    requested_at: datetime.datetime
    token: str


@dataclass
class LiveGrant:
    target: str
    granted_at: datetime.datetime
    ttl_minutes: int

    def expired(self) -> bool:
        age = datetime.datetime.now(datetime.timezone.utc) - self.granted_at
        return age.total_seconds() > self.ttl_minutes * 60


class SandboxController:
    def __init__(self, config: dict, audit_log: AuditLog):
        self.config = config
        self.audit = audit_log
        self._pending: PendingConfirmation | None = None
        self._live: LiveGrant | None = None

    @property
    def is_live(self) -> bool:
        return self._live is not None and not self._live.expired()

    def current_state(self) -> str:
        if self.is_live:
            return f"LIVE[{self._live.target}]"
        if self._pending:
            return f"CONFIRM[{self._pending.target}]"
        return "SANDBOX"

    def request_go_live(self, target: str, owner_attestation: bool = False) -> str:
        if not _looks_like_private_target(target) and not owner_attestation:
            self.audit.write("go_live_denied", target=target, reason="public target, no attestation")
            return f"REFUSED: '{target}' doesn't look like a private/lab target. Provide owner_attestation=True if you own it."
        token = uuid.uuid4().hex[:8]
        self._pending = PendingConfirmation(target=target, requested_at=datetime.datetime.now(datetime.timezone.utc), token=token)
        self.audit.write("go_live_requested", target=target, token=token)
        return f"Confirm Go-Live for '{target}' by calling confirm_go_live with token '{token}'."

    def confirm_go_live(self, target: str, token: str) -> str:
        if not self._pending or self._pending.target != target or self._pending.token != token:
            self.audit.write("go_live_denied", target=target, reason="bad token or no pending")
            return "REFUSED: invalid or expired confirmation token."
        ttl = int(self.config.get("live_mode_ttl_minutes", 30))
        self._live = LiveGrant(target=target, granted_at=datetime.datetime.now(datetime.timezone.utc), ttl_minutes=ttl)
        self._pending = None
        self.audit.write("go_live_granted", target=target, ttl_minutes=ttl)
        return f"LIVE granted for '{target}' for {ttl} minutes."

    def stand_down(self) -> str:
        if self._live:
            self.audit.write("go_live_revoked", target=self._live.target)
        self._live = None
        self._pending = None
        return "Back to SANDBOX."

    def run_security_tool(self, command: str, args: list[str], target: str) -> str:
        if command not in ALLOWED_SANDBOX_CMDS:
            return f"REFUSED: '{command}' is not allow-listed"
        live = self.is_live and self._live.target == target
        safe_args = [a for a in args if not re.search(r"[;&|`$]", a)]
        argv = [command, *safe_args]
        if live:
            self.audit.write("live_tool_run", command=command, args=safe_args, target=target)
            try:
                proc = subprocess.run(argv, capture_output=True, text=True, timeout=120)
                return (proc.stdout or "")[-5000:] + ((proc.stderr or "")[-2000:] if proc.returncode else "")
            except Exception as e:
                return f"ERROR: {e}"
        self.audit.write("sandbox_tool_run", command=command, args=safe_args, target=target)
        docker_cmd = ["docker", "run", "--rm", "--network", "none",
                      "--cpus", str(self.config.get("cpu_limit", "1.0")),
                      "--memory", self.config.get("mem_limit", "1g"),
                      self.config.get("docker_image", "friday-sandbox:latest"), *argv]
        try:
            proc = subprocess.run(docker_cmd, capture_output=True, text=True,
                                   timeout=self.config.get("default_timeout_seconds", 60))
            return (proc.stdout or "")[-5000:] + ((proc.stderr or "")[-2000:] if proc.returncode else "")
        except FileNotFoundError:
            return "ERROR: Docker not available"
        except subprocess.TimeoutExpired:
            return "ERROR: timed out"
