"""
F.R.I.D.A.Y native desktop entrypoint.
- Starts the local API in a background thread
- Opens a NATIVE OS window via pywebview (NOT a browser)
- 100% local: 127.0.0.1 only
"""
from __future__ import annotations

import sys
import threading
import time


def _run_server():
    import uvicorn
    from app.main import app, config
    uvicorn.run(
        app,
        host=config.get("server", {}).get("host", "127.0.0.1"),
        port=int(config.get("server", {}).get("port", 8787)),
        log_level="warning",
    )


def main():
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    # Wait until health responds
    import urllib.request
    url = "http://127.0.0.1:8787/health"
    for _ in range(60):
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.5)

    import webview
    webview.create_window(
        "F.R.I.D.A.Y",
        "http://127.0.0.1:8787/hud/",
        width=1280,
        height=800,
        confirm_close=True,
    )
    webview.start()
    # Window closed -> exit process (daemon server dies with it)
    sys.exit(0)


if __name__ == "__main__":
    main()
