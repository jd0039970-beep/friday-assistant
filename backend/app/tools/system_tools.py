"""Filesystem, screenshot, clipboard, process tools."""
from __future__ import annotations

import os
from pathlib import Path

from .registry import ToolRegistry

HOME = Path.home()


def register_system_tools(reg: ToolRegistry):
    def list_dir(path: str = "~") -> str:
        p = Path(path).expanduser().resolve()
        if not str(p).startswith(str(HOME)):
            return "REFUSED: path outside home directory"
        if not p.exists():
            return f"Not found: {p}"
        items = sorted(p.iterdir())[:100]
        return "\n".join(f"{'[DIR]' if i.is_dir() else '[FILE]'} {i.name}" for i in items)

    def read_file(path: str) -> str:
        p = Path(path).expanduser().resolve()
        if not str(p).startswith(str(HOME)):
            return "REFUSED: path outside home"
        return p.read_text(encoding="utf-8", errors="replace")[:8000]

    def take_screenshot() -> str:
        try:
            import pyautogui
            from tempfile import NamedTemporaryFile
            f = NamedTemporaryFile(suffix=".png", delete=False)
            pyautogui.screenshot(f.name)
            return f"Screenshot saved to {f.name}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def get_clipboard() -> str:
        try:
            import pyperclip
            return pyperclip.paste()[:4000]
        except Exception as e:
            return f"Clipboard error: {e}"

    def list_processes() -> str:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
            try:
                procs.append(f"{p.info['pid']:>6}  {p.info['name'][:40]:<40}  {p.info['cpu_percent']}%")
            except Exception:
                continue
        return "PID     NAME                                      CPU\n" + "\n".join(procs[:40])

    reg.register("list_dir", "List files in a directory (home-scoped)",
                 {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}, list_dir)
    reg.register("read_file", "Read a text file (home-scoped)",
                 {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, read_file)
    reg.register("take_screenshot", "Capture the current screen",
                 {"type": "object", "properties": {}}, take_screenshot)
    reg.register("get_clipboard", "Get current clipboard text",
                 {"type": "object", "properties": {}}, get_clipboard)
    reg.register("list_processes", "List running processes",
                 {"type": "object", "properties": {}}, list_processes)
