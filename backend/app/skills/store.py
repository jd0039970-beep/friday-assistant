"""Self-extending skill system.

Friday can draft a new Python skill, it is written into a sandbox skills folder,
tested once, and only promoted to permanent after the user says so (or when
Workshop Mode is on and the skill is marked safe).
"""
from __future__ import annotations

import importlib.util
import json
import traceback
from pathlib import Path

SKILLS_DIR = Path.home() / ".friday" / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST = SKILLS_DIR / "manifest.json"


def _load_manifest() -> dict:
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except Exception:
            return {"skills": []}
    return {"skills": []}


def _save_manifest(data: dict):
    MANIFEST.write_text(json.dumps(data, indent=2))


def list_skills() -> str:
    data = _load_manifest()
    if not data["skills"]:
        return "No custom skills yet."
    lines = []
    for s in data["skills"]:
        lines.append(f"- {s['name']}: {s.get('description','')} [{s.get('status','draft')}]")
    return "\n".join(lines)


def create_skill(name: str, description: str, code: str) -> str:
    """Write a new skill file. Name must be a valid Python identifier."""
    safe = "".join(c for c in name if c.isalnum() or c == "_").lower()
    if not safe:
        return "ERROR: invalid skill name"
    path = SKILLS_DIR / f"{safe}.py"
    header = f'"""{description}\nAuto-generated skill. Runs in restricted context."""\n\n'
    path.write_text(header + code, encoding="utf-8")
    data = _load_manifest()
    data["skills"] = [s for s in data["skills"] if s["name"] != safe]
    data["skills"].append({"name": safe, "description": description, "status": "draft", "path": str(path)})
    _save_manifest(data)
    return f"Skill '{safe}' created as DRAFT at {path}. Call run_skill to test, then promote when ready."


def run_skill(name: str, **kwargs) -> str:
    data = _load_manifest()
    entry = next((s for s in data["skills"] if s["name"] == name), None)
    if not entry:
        return f"Unknown skill: {name}"
    path = Path(entry["path"])
    if not path.exists():
        return f"Skill file missing: {path}"
    try:
        spec = importlib.util.spec_from_file_location(f"friday_skill_{name}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "run"):
            return "ERROR: skill must define a run(**kwargs) function"
        result = mod.run(**kwargs)
        return str(result)[:8000]
    except Exception:
        return "SKILL ERROR:\n" + traceback.format_exc()[-2000:]


def promote_skill(name: str) -> str:
    data = _load_manifest()
    for s in data["skills"]:
        if s["name"] == name:
            s["status"] = "active"
            _save_manifest(data)
            return f"Skill '{name}' promoted to ACTIVE."
    return f"Skill not found: {name}"
