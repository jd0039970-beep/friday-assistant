"""Full voice pipeline: record → STT → (agent) → TTS → play."""
from __future__ import annotations

import tempfile
import wave
from pathlib import Path

from .stt import FasterWhisperSTT
from .tts import PiperTTS


class VoicePipeline:
    def __init__(self, stt_model: str = "small.en", tts_voice: str = "en_GB-alba-medium"):
        self.stt = FasterWhisperSTT(model_size=stt_model)
        self.tts = PiperTTS(voice=tts_voice)

    def record_seconds(self, seconds: float = 5.0, sample_rate: int = 16000) -> str:
        """Record from default microphone and return path to WAV."""
        try:
            import sounddevice as sd
            import numpy as np
            print(f"[Friday] Listening for {seconds}s...")
            audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()
            path = Path(tempfile.gettempdir()) / "friday_input.wav"
            with wave.open(str(path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
            return str(path)
        except Exception as e:
            raise RuntimeError(f"Recording failed: {e}")

    def listen(self, seconds: float = 5.0) -> str:
        """Record then transcribe."""
        wav = self.record_seconds(seconds)
        return self.stt.transcribe(wav)

    def speak(self, text: str) -> str:
        """Synthesize and play. Returns path to WAV."""
        wav_path = self.tts.synthesize(text)
        try:
            import sounddevice as sd
            import soundfile as sf
            data, sr = sf.read(wav_path)
            sd.play(data, sr)
            sd.wait()
        except Exception:
            # fallback: just leave the file
            pass
        return wav_path
