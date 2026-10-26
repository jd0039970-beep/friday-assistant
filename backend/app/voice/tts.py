"""Piper TTS wrapper for local British female voice."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


class PiperTTS:
    def __init__(self, voice: str = "en_GB-alba-medium", piper_bin: str = "piper"):
        self.voice = voice
        self.piper_bin = piper_bin

    def synthesize(self, text: str) -> str:
        """Returns path to generated WAV file."""
        out_path = Path(tempfile.gettempdir()) / f"friday_tts_{abs(hash(text))}.wav"
        subprocess.run(
            [self.piper_bin, "--model", self.voice, "--output_file", str(out_path)],
            input=text, text=True, check=True,
        )
        return str(out_path)
