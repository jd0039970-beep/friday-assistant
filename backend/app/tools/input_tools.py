"""Mouse, keyboard, window control tools."""
from __future__ import annotations

from .registry import ToolRegistry


def register_input_tools(reg: ToolRegistry):
    def type_text(text: str) -> str:
        try:
            import pyautogui
            pyautogui.write(text, interval=0.02)
            return f"Typed {len(text)} characters"
        except Exception as e:
            return f"Type failed: {e}"

    def click(x: int, y: int, button: str = "left") -> str:
        try:
            import pyautogui
            pyautogui.click(x, y, button=button)
            return f"Clicked {button} at ({x},{y})"
        except Exception as e:
            return f"Click failed: {e}"

    def move_mouse(x: int, y: int) -> str:
        try:
            import pyautogui
            pyautogui.moveTo(x, y)
            return f"Moved mouse to ({x},{y})"
        except Exception as e:
            return f"Move failed: {e}"

    def press_key(key: str) -> str:
        try:
            import pyautogui
            pyautogui.press(key)
            return f"Pressed {key}"
        except Exception as e:
            return f"Key failed: {e}"

    reg.register("type_text", "Type text via keyboard",
                 {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}, type_text, requires_confirmation=True)
    reg.register("click", "Click at screen coordinates",
                 {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "button": {"type": "string"}}, "required": ["x", "y"]}, click, requires_confirmation=True)
    reg.register("move_mouse", "Move mouse cursor",
                 {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}, move_mouse)
    reg.register("press_key", "Press a single key (e.g. enter, esc, tab)",
                 {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}, press_key, requires_confirmation=True)
