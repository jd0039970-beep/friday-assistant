"""Workshop Mode + trusted targets.

Tony-Stark style: enable Workshop Mode once (typed). After that, targets on the
trusted list run with no extra confirmation. Random public internet is still
refused unless explicitly attested. This removes permission spam for your own
lab without turning Friday into an open attack tool.
"""
from __future__ import annotations

import json
from pathlib import Path

STATE_PATH = Path.home() / ".friday" / "workshop.json"


class WorkshopState:
    def __init__(self):
        self.enabled: bool = False
        self.trusted: list[str] = []
        self._load()

    def _load(self):
        if STATE_PATH.exists():
            try:
                data = json.loads(STATE_PATH.read_text())
                self.enabled = bool(data.get("enabled", False))
                self.trusted = list(data.get("trusted", []))
            except Exception:
                pass

    def _save(self):
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps({"enabled": self.enabled, "trusted": self.trusted}, indent=2))

    def enable(self) -> str:
        self.enabled = True
        self._save()
        return "Workshop Mode ENABLED. Trusted lab targets will run without repeated confirmation. Public internet still requires attestation."

    def disable(self) -> str:
        self.enabled = False
        self._save()
        return "Workshop Mode disabled. Back to strict sandbox."

    def add_trusted(self, target: str) -> str:
        t = target.strip()
        if t not in self.trusted:
            self.trusted.append(t)
            self._save()
        return f"Trusted target added: {t}. Total trusted: {len(self.trusted)}"

    def is_trusted(self, target: str) -> bool:
        return self.enabled and target.strip() in self.trusted
