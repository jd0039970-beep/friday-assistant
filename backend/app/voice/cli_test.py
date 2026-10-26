"""Quick voice loop test: python -m app.voice.cli_test"""
from __future__ import annotations

import sys
from pathlib import Path

# allow running from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.voice.pipeline import VoicePipeline


def main():
    pipe = VoicePipeline(stt_model="small.en", tts_voice="en_GB-alba-medium")
    print("F.R.I.D.A.Y voice test. Speak after the prompt. Ctrl+C to quit.")
    while True:
        try:
            text = pipe.listen(seconds=4.0)
            print(f"You: {text}")
            if not text.strip():
                continue
            reply = f"I heard: {text}"
            print(f"Friday: {reply}")
            pipe.speak(reply)
        except KeyboardInterrupt:
            print("\nStand down.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
