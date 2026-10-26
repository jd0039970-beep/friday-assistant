"""Boot-time system check and skill smoke tests."""
from __future__ import annotations

import importlib
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class BootReport:
    started_at: float = field(default_factory=time.time)
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = ""):
        self.checks.append(CheckResult(name, ok, detail))

    @property
    def all_ok(self) -> bool:
        return all(c.ok for c in self.checks)

    def summary(self) -> str:
        lines = ["F.R.I.D.A.Y boot check", "=" * 40]
        for c in self.checks:
            flag = "OK " if c.ok else "FAIL"
            lines.append(f"  [{flag}] {c.name}" + (f" — {c.detail}" if c.detail else ""))
        lines.append("=" * 40)
        lines.append("ALL GREEN" if self.all_ok else "ISSUES DETECTED — see FAIL lines")
        lines.append(f"Elapsed: {time.time() - self.started_at:.1f}s")
        return "\n".join(lines)


def _has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def run_boot_check(
    *,
    ollama_url: str = "http://localhost:11434",
    test_tools: dict[str, Callable] | None = None,
) -> BootReport:
    report = BootReport()

    # Core Python deps
    for mod in ("fastapi", "httpx", "yaml", "numpy", "PIL"):
        try:
            importlib.import_module(mod if mod != "PIL" else "PIL")
            report.add(f"python:{mod}", True)
        except Exception as e:
            report.add(f"python:{mod}", False, str(e))

    # Optional but important
    for mod, label in (
        ("faster_whisper", "stt"),
        ("playwright", "web"),
        ("docker", "docker-sdk"),
    ):
        try:
            importlib.import_module(mod)
            report.add(f"python:{label}", True)
        except Exception as e:
            report.add(f"python:{label}", False, str(e))

    # External binaries
    report.add("bin:ollama", _has_cmd("ollama"), "not in PATH" if not _has_cmd("ollama") else "")
    report.add("bin:docker", _has_cmd("docker"), "sandbox limited without docker" if not _has_cmd("docker") else "")
    report.add("bin:tesseract", _has_cmd("tesseract"), "OCR limited" if not _has_cmd("tesseract") else "")

    # Ollama reachability
    try:
        import httpx
        r = httpx.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=3.0)
        report.add("ollama:api", r.status_code == 200, f"status {r.status_code}")
    except Exception as e:
        report.add("ollama:api", False, str(e))

    # Paths
    friday_home = Path.home() / ".friday"
    try:
        friday_home.mkdir(parents=True, exist_ok=True)
        report.add("fs:~/.friday", True)
    except Exception as e:
        report.add("fs:~/.friday", False, str(e))

    # Skill smoke tests (safe, no Live, no network attacks)
    if test_tools:
        for name, fn in test_tools.items():
            try:
                out = fn()
                ok = out is not None and not str(out).startswith("ERROR")
                report.add(f"skill:{name}", ok, str(out)[:120])
            except Exception as e:
                report.add(f"skill:{name}", False, str(e))

    return report
