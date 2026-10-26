"""Filesystem, screenshot, clipboard, process, notification tools."""
from __future__ import annotations

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
        items = sorted(p.iterdir())[:120]
        return "\n".join(f"{'[DIR]' if i.is_dir() else '[FILE]'} {i.name}" for i in items)

    def read_file(path: str) -> str:
        p = Path(path).expanduser().resolve()
        if not str(p).startswith(str(HOME)):
            return "REFUSED: path outside home"
        try:
            return p.read_text(encoding="utf-8", errors="replace")[:10000]
        except Exception as e:
            return f"ERROR: {e}"

    def write_file(path: str, content: str) -> str:
        p = Path(path).expanduser().resolve()
        if not str(p).startswith(str(HOME)):
            return "REFUSED: path outside home"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} chars to {p}"

    def get_clipboard() -> str:
        try:
            import pyperclip
            return pyperclip.paste()[:5000]
        except Exception as e:
            return f"Clipboard error: {e}"

    def set_clipboard(text: str) -> str:
        try:
            import pyperclip
            pyperclip.copy(text)
            return "Clipboard updated"
        except Exception as e:
            return f"Clipboard error: {e}"

    def list_processes() -> str:
        import psutil
        lines = ["PID     NAME                                      CPU%"]
        for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
            try:
                info = p.info
                lines.append(f"{info['pid']:>6}  {str(info['name'])[:40]:<40}  {info['cpu_percent']}")
            except Exception:
                continue
        return "\n".join(lines[:50])

    def notify(title: str, message: str) -> str:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_name="F.R.I.D.A.Y", timeout=5)
            return "Notification sent"
        except Exception as e:
            return f"Notify failed: {e}"

    def system_info() -> str:
        import platform, psutil
        return (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Machine: {platform.machine()}\n"
            f"CPU cores: {psutil.cpu_count()}\n"
            f"RAM: {psutil.virtual_memory().total // (1024**3)} GB\n"
            f"Disk free: {psutil.disk_usage('/').free // (1024**3)} GB"
        )

    reg.register("list_dir", "List files in a directory (home-scoped)",
                 {"type": "object", "properties": {"path": {"type": "string"}}}, list_dir)
    reg.register("read_file", "Read a text file (home-scoped)",
                 {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}, read_file)
    reg.register("write_file", "Write text to a file (home-scoped, asks confirmation)",
                 {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}, write_file, requires_confirmation=True)
    reg.register("get_clipboard", "Get current clipboard text",
                 {"type": "object", "properties": {}}, get_clipboard)
    reg.register("set_clipboard", "Set clipboard text",
                 {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}, set_clipboard)
    reg.register("list_processes", "List running processes",
                 {"type": "object", "properties": {}}, list_processes)
    reg.register("notify", "Show a desktop notification",
                 {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}}, "required": ["title", "message"]}, notify)
    reg.register("system_info", "Basic system information",
                 {"type": "object", "properties": {}}, system_info)
