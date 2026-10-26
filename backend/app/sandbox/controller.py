"""Sandbox / Go-Live state machine.

For offline / forensics lab use (encrypted drives, air-gapped or wired-only
machines) there is no public-target block. Workshop Mode + trusted list still
exist for convenience, but any local path, block device, or private IP can go
live without ownership attestation.
"""
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
ALLOWED_SANDBOX_CMDS = {
    "nmap", "hashcat", "john", "binwalk", "strings", "file",
    "testdisk", "photorec", "foremost", "bulk_extractor",
}


def _is_local_or_private(target: str) -> bool:
    """True for local paths, block devices, localhost, private IPs."""
    t = target.strip()
    # filesystem / block device
    if t.startswith("/") or t.startswith("./") or t.startswith("~") or ":\\" in t or t.startswith("\\\\.\\"):
        return True
    if t.lower().startswith(("/dev/", "\\.\\physicaldrive", "physicaldrive")):
        return True
    host = t.split("/")[0].split(":")[0]
    try:
        ip = ipaddress.ip_address(host)
        return any(ip in net for net in PRIVATE_NETS)
    except ValueError:
        return host in ("localhost",) or host.endswith(".local")


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
        # When True, any target can go live (for fully offline / wired-only labs)
        self.unrestricted_local: bool = bool(config.get("unrestricted_local", True))

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
        # Local paths, block devices, private IPs: always allowed.
        # Public IPs: allowed when unrestricted_local is on (offline/wired lab),
        # or when owner_attestation is explicitly True.
        if not _is_local_or_private(target) and not self.unrestricted_local and not owner_attestation:
            self.audit.write("go_live_denied", target=target, reason="public target, attestation required")
            return (
                f"REFUSED: '{target}' looks public and unrestricted_local is off. "
                "Either enable unrestricted_local in config, or pass owner_attestation=True."
            )

        token = uuid.uuid4().hex[:8]
        self._pending = PendingConfirmation(
            target=target,
            requested_at=datetime.datetime.now(datetime.timezone.utc),
            token=token,
        )
        self.audit.write("go_live_requested", target=target, token=token)
        return f"Confirm Go-Live for '{target}' with token '{token}'."

    def confirm_go_live(self, target: str, token: str) -> str:
        if not self._pending or self._pending.target != target or self._pending.token != token:
            self.audit.write("go_live_denied", target=target, reason="bad token")
            return "REFUSED: invalid or expired token."
        ttl = int(self.config.get("live_mode_ttl_minutes", 60))
        self._live = LiveGrant(
            target=target,
            granted_at=datetime.datetime.now(datetime.timezone.utc),
            ttl_minutes=ttl,
        )
        self._pending = None
        self.audit.write("go_live_granted", target=target, ttl_minutes=ttl)
        return f"LIVE granted for '{target}' ({ttl} min)."

    def stand_down(self) -> str:
        if self._live:
            self.audit.write("go_live_revoked", target=self._live.target)
        self._live = None
        self._pending = None
        return "Back to SANDBOX."

    def run_security_tool(self, command: str, args: list[str], target: str) -> str:
        if command not in ALLOWED_SANDBOX_CMDS:
            return f"REFUSED: '{command}' not in allow-list"

        live = self.is_live and self._live.target == target
        safe_args = [a for a in args if not re.search(r"[;&|`$]", a)]
        argv = [command, *safe_args]

        if live:
            self.audit.write("live_tool_run", command=command, args=safe_args, target=target)
            try:
                proc = subprocess.run(argv, capture_output=True, text=True, timeout=300)
                out = (proc.stdout or "")[-8000:]
                err = (proc.stderr or "")[-2000:] if proc.returncode else ""
                return out + err
            except Exception as e:
                return f"ERROR: {e}"

        # Sandbox (Docker, no network)
        self.audit.write("sandbox_tool_run", command=command, args=safe_args, target=target)
        docker_cmd = [
            "docker", "run", "--rm", "--network", "none",
            "--cpus", str(self.config.get("cpu_limit", "1.5")),
            "--memory", self.config.get("mem_limit", "1.5g"),
            "-v", f"{target}:{target}:ro" if target.startswith("/") else "",
            self.config.get("docker_image", "friday-sandbox:latest"),
            *argv,
        ]
        docker_cmd = [c for c in docker_cmd if c]  # drop empty volume if not a path
        try:
            proc = subprocess.run(
                docker_cmd, capture_output=True, text=True,
                timeout=self.config.get("default_timeout_seconds", 120),
            )
            return ((proc.stdout or "") + (proc.stderr or ""))[-8000:]
        except FileNotFoundError:
            return "ERROR: Docker not available — cannot sandbox. Enable live mode for this target or install Docker."
        except subprocess.TimeoutExpired:
            return "ERROR: sandboxed command timed out"
