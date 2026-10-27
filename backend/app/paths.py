"""Resolve project paths for dev and PyInstaller frozen exe."""
from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Folder that contains config/ and frontend/."""
    if getattr(sys, "frozen", False):
        # PyInstaller onedir: exe lives in dist/Friday/; we also copy config+hud beside it
        meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        # Prefer folder next to the exe (we add-data into the bundle too)
        exe_dir = Path(sys.executable).resolve().parent
        for candidate in (exe_dir, meipass, exe_dir.parent):
            if (candidate / "config" / "config.yaml").exists():
                return candidate
            if (candidate / "frontend" / "hud").exists():
                return candidate
        return exe_dir
    # Dev: backend/app/paths.py -> parents[2] = repo root
    return Path(__file__).resolve().parents[2]


def config_path() -> Path:
    return app_root() / "config" / "config.yaml"


def hud_dir() -> Path:
    return app_root() / "frontend" / "hud"
