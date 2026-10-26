"""Select only the relevant tool groups for a turn so the model is not flooded."""
from __future__ import annotations

# Categories the agent can pull from. The router picks a subset per message.
CATEGORIES = {
    "core": ["list_dir", "read_file", "write_file", "get_clipboard", "set_clipboard",
             "notify", "system_info", "list_processes"],
    "input": ["type_text", "click", "move_mouse", "press_key"],
    "vision": ["what_is_on_screen", "take_screenshot", "capture_webcam"],
    "web": ["browse_url", "search_web"],
    "security": ["request_go_live", "confirm_go_live", "stand_down", "run_nmap",
                 "enable_workshop_mode", "add_trusted_target"],
    "skills": ["list_skills", "create_skill", "run_skill"],
}

KEYWORDS = {
    "input": ["click", "type", "typewriter", "keyboard", "mouse", "press", "hotkey", "window"],
    "vision": ["screen", "see", "look", "ocr", "webcam", "camera", "what's on", "what is on"],
    "web": ["browse", "search", "google", "url", "website", "http", "web"],
    "security": ["scan", "nmap", "hack", "port", "hash", "crack", "binwalk", "live", "sandbox",
                 "workshop", "trusted", "lab"],
    "skills": ["skill", "new tool", "create tool", "add ability", "learn how"],
}


def select_tools(user_message: str, all_schemas: list[dict]) -> list[dict]:
    """Return a reduced schema list for this turn."""
    msg = user_message.lower()
    chosen = set(CATEGORIES["core"])  # always available

    for cat, keys in KEYWORDS.items():
        if any(k in msg for k in keys):
            chosen.update(CATEGORIES.get(cat, []))

    # if nothing special matched, still give vision + web lightly
    if chosen == set(CATEGORIES["core"]):
        chosen.update(CATEGORIES["vision"][:1])  # what_is_on_screen
        chosen.update(["search_web"])

    name_set = chosen
    return [s for s in all_schemas if s.get("function", {}).get("name") in name_set]
