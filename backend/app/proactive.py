"""Proactive hooks — optional background awareness.

When enabled, Friday can notice new block devices and surface a suggestion.
Runs as a lightweight poller; does not auto-Live anything.
"""
from __future__ import annotations

import subprocess
import threading
import time
from pathlib import Path


class ProactiveMonitor:
    def __init__(self, interval: float = 15.0):
        self.interval = interval
        self._seen: set[str] = set()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.suggestions: list[str] = []

    def _list_block_devices(self) -> set[str]:
        devices = set()
        try:
            # Linux
            out = subprocess.check_output(["lsblk", "-ndo", "NAME,TYPE"], text=True, timeout=5)
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "disk":
                    devices.add("/dev/" + parts[0])
        except Exception:
            pass
        # Also watch common image drop folders
        drop = Path.home() / "friday_inbox"
        if drop.exists():
            for p in drop.iterdir():
                if p.is_file():
                    devices.add(str(p))
        return devices

    def _loop(self):
        self._seen = self._list_block_devices()
        while not self._stop.is_set():
            time.sleep(self.interval)
            current = self._list_block_devices()
            new = current - self._seen
            for d in new:
                msg = f"New device or image detected: {d}. Say 'work on {d}' if you want me to identify it."
                self.suggestions.append(msg)
                print(f"[Friday proactive] {msg}")
            self._seen = current

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def pop_suggestions(self) -> list[str]:
        out = list(self.suggestions)
        self.suggestions.clear()
        return out
