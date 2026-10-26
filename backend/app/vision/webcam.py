"""Webcam capture (optional)."""
from __future__ import annotations

import tempfile
from pathlib import Path


def capture_webcam(camera_index: int = 0) -> str:
    """Capture a single frame from the default webcam. Returns file path or error."""
    try:
        import cv2
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return "ERROR: cannot open webcam"
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "ERROR: failed to capture frame"
        fd, path = tempfile.mkstemp(suffix=".jpg", prefix="friday_cam_")
        import os
        os.close(fd)
        cv2.imwrite(path, frame)
        return path
    except ImportError:
        return "ERROR: opencv-python not installed (pip install opencv-python-headless)"
    except Exception as e:
        return f"ERROR: webcam capture failed: {e}"
