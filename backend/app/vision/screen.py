"""Screen capture + OCR."""
from __future__ import annotations

from pathlib import Path
import tempfile


def capture_screenshot(path: str | None = None) -> str:
    """Take a screenshot and return the file path."""
    try:
        import pyautogui
        if path is None:
            fd, path = tempfile.mkstemp(suffix=".png", prefix="friday_screen_")
            import os
            os.close(fd)
        pyautogui.screenshot(path)
        return path
    except Exception as e:
        return f"ERROR: screenshot failed: {e}"


def ocr_image(image_path: str, lang: str = "eng") -> str:
    """Run Tesseract OCR on an image and return extracted text."""
    try:
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(image_path), lang=lang)
        return text.strip() or "(no text detected)"
    except Exception as e:
        return f"ERROR: OCR failed: {e}. Is tesseract installed?"


def screen_text(lang: str = "eng") -> str:
    """Screenshot + OCR in one call."""
    path = capture_screenshot()
    if path.startswith("ERROR"):
        return path
    text = ocr_image(path, lang=lang)
    return f"[Screenshot: {path}]\n{text}"
