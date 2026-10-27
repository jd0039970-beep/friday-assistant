"""
F.R.I.D.A.Y native desktop entrypoint.
Starts local API + native pywebview window. Logs failures to Desktop.
"""
from __future__ import annotations

import sys
import threading
import time
import traceback
from pathlib import Path


def _log(msg: str) -> None:
    line = msg.rstrip() + "\n"
    print(line, end="")
    try:
        log = Path.home() / "Desktop" / "friday_error.log"
        with open(log, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        try:
            log = Path.home() / "friday_error.log"
            with open(log, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass


def _run_server():
    try:
        import uvicorn
        from app.main import app, config
        host = config.get("server", {}).get("host", "127.0.0.1")
        port = int(config.get("server", {}).get("port", 8787))
        _log(f"Server starting on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception:
        _log("SERVER CRASH:\n" + traceback.format_exc())


def main():
    _log("F.R.I.D.A.Y desktop starting...")
    try:
        t = threading.Thread(target=_run_server, daemon=True)
        t.start()

        import urllib.request
        url = "http://127.0.0.1:8787/health"
        ready = False
        for i in range(90):
            try:
                with urllib.request.urlopen(url, timeout=1) as r:
                    if r.status == 200:
                        ready = True
                        _log("Backend healthy.")
                        break
            except Exception:
                time.sleep(0.5)
        if not ready:
            _log("Backend did not become healthy in time. See log above.")

        import webview
        webview.create_window(
            "F.R.I.D.A.Y",
            "http://127.0.0.1:8787/hud/",
            width=1280,
            height=800,
            confirm_close=True,
        )
        webview.start()
        _log("Window closed.")
        sys.exit(0)
    except Exception:
        _log("DESKTOP CRASH:\n" + traceback.format_exc())
        # Keep console open on failure
        try:
            input("Press Enter to close...")
        except Exception:
            time.sleep(30)
        sys.exit(1)


if __name__ == "__main__":
    main()
