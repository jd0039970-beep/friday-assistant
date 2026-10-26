"""Controlled shell execution for lab workflows.

Friday can run allow-listed commands herself. Destructive or privileged
commands still go through Live / confirmation when required.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .registry import ToolRegistry

HOME = Path.home()

# Commands Friday may run directly on the host when in Live or for pure local work
ALLOW = {
    "ls", "cat", "head", "tail", "file", "strings", "sha256sum", "md5sum",
    "diskutil", "lsblk", "fdisk", "mount", "umount", "dd",
    "python3", "python", "pip", "which", "uname", "df", "du",
}


def register_shell_tools(reg: ToolRegistry):
    def run_command(command: str, cwd: str | None = None) -> str:
        """Run a single allow-listed command. No shell metacharacters."""
        try:
            parts = shlex.split(command)
        except ValueError as e:
            return f"ERROR: bad command string: {e}"
        if not parts:
            return "ERROR: empty command"
        bin_name = Path(parts[0]).name
        if bin_name not in ALLOW:
            return f"REFUSED: '{bin_name}' not in allow-list. Use a specific tool or expand ALLOW."

        workdir = str(Path(cwd).expanduser()) if cwd else str(HOME)
        try:
            proc = subprocess.run(
                parts, capture_output=True, text=True, cwd=workdir, timeout=120,
            )
            out = (proc.stdout or "")[-6000:]
            err = (proc.stderr or "")[-1500:] if proc.returncode else ""
            return out + err or f"(exit {proc.returncode}, no output)"
        except subprocess.TimeoutExpired:
            return "ERROR: command timed out"
        except Exception as e:
            return f"ERROR: {e}"

    reg.register(
        "run_command",
        "Run an allow-listed local command (ls, file, strings, lsblk, python3, ...)",
        {"type": "object", "properties": {
            "command": {"type": "string"},
            "cwd": {"type": "string"},
        }, "required": ["command"]},
        run_command,
    )
