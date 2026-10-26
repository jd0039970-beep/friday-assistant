"""faster-whisper STT wrapper."""
from __future__ import annotations

from pathlib import Path


class FasterWhisperSTT:
    def __init__(self, model_size: str = "small.en"):
        self.model_size = model_size
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def transcribe(self, audio_path: str) -> str:
        model = self._load()
        segments, _ = model.transcribe(audio_path, beam_size=5)
        return " ".join(s.text.strip() for s in segments).strip()

    def transcribe_bytes(self, data: bytes, suffix: str = ".webm") -> str:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(data)
            path = f.name
        try:
            return self.transcribe(path)
        finally:
            try:
                Path(path).unlink(missing_ok=True)
            except Exception:
                pass
