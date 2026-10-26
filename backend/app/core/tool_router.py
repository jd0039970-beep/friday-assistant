"""Select only relevant tool groups so the small model is not flooded."""
from __future__ import annotations

CATEGORIES = {
    "core": [
        "list_dir", "read_file", "write_file", "get_clipboard", "set_clipboard",
        "notify", "system_info", "list_processes", "run_command",
    ],
    "input": ["type_text", "click", "move_mouse", "press_key"],
    "vision": ["what_is_on_screen", "take_screenshot", "capture_webcam"],
    "web": ["browse_url", "search_web"],
    "security": [
        "request_go_live", "confirm_go_live", "stand_down",
        "run_nmap", "run_hashcat", "run_john", "run_binwalk", "run_file", "run_strings",
        "enable_workshop_mode", "add_trusted_target", "list_trusted",
    ],
    "skills": ["list_skills", "create_skill", "run_skill", "promote_skill"],
}

KEYWORDS = {
    "input": ["click", "type", "keyboard", "mouse", "press", "hotkey", "window"],
    "vision": ["screen", "see", "look", "ocr", "webcam", "camera", "what's on", "what is on"],
    "web": ["browse", "search", "google", "url", "website", "http"],
    "security": [
        "scan", "nmap", "hack", "port", "hash", "crack", "binwalk", "john", "hashcat",
        "live", "sandbox", "workshop", "trusted", "lab", "encrypt", "drive", "disk",
        "forensic", "firmware", "password", "wordlist",
    ],
    "skills": ["skill", "new tool", "create tool", "add ability", "learn how"],
}


def select_tools(user_message: str, all_schemas: list[dict]) -> list[dict]:
    msg = user_message.lower()
    chosen = set(CATEGORIES["core"])
    for cat, keys in KEYWORDS.items():
        if any(k in msg for k in keys):
            chosen.update(CATEGORIES.get(cat, []))
    if chosen == set(CATEGORIES["core"]):
        chosen.update(["what_is_on_screen", "search_web"])
    return [s for s in all_schemas if s.get("function", {}).get("name") in chosen]
