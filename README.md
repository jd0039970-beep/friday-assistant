# F.R.I.D.A.Y — Local Iron-Man AI

**Fully local · holographic HUD · voice · vision · PC control · Workshop Mode · self-skills**

A Tony-Stark-style desktop AI that runs on your machine. Blue holographic interface,
British-female voice (Piper), full computer control, screen vision, web access, and a
sandboxed security module that can go live on **your** lab targets.

## Quick start

```bash
git clone https://github.com/jd0039970-beep/friday-assistant.git
cd friday-assistant
bash scripts/install.sh          # or scripts/install.ps1 on Windows

cd backend && source .venv/bin/activate
python -m app.main
```

Then open the HUD:

```
http://127.0.0.1:8787/hud/
```

## Holographic HUD

Animated blue circular core (inspired by classic JARVIS rings, rebranded FRIDAY),
particle field, side system panels, conversation stream, and holographic result cards
when she shows you scan output, code, or files.

## Workshop Mode (no permission spam)

```
You: enable workshop mode
Friday: Workshop Mode ENABLED...

You: add trusted target 192.168.1.50
Friday: Trusted target added.

You: scan 192.168.1.50
Friday: (runs nmap live, no extra prompts)
```

Public internet targets still require explicit attestation. Your lab does not.

## Self-skills

```
You: create a skill that converts markdown to plain text
Friday: (writes skill, tests it)
You: promote that skill
```

Skills live in `~/.friday/skills/` and can be reused forever.

## Voice

```bash
pip install piper-tts
python -m piper.download_voices en_GB-alba-medium
python -m app.voice.cli_test
```

## Safety (the only guardrails)

- Default = Docker sandbox, no network
- Workshop Mode + trusted list = smooth lab work
- Voice can never escalate privileges
- No OS privilege escalation by the agent itself
- Append-only audit log at `~/.friday/audit.log`

## Stack

- Brain: Qwen2.5-7B via Ollama (3B fallback)
- Voice: faster-whisper + Piper `en_GB-alba-medium`
- Vision: screenshot + Tesseract, webcam
- Web: Playwright
- UI: pure HTML/CSS/JS holographic HUD (Tauri shell later)

MIT licensed. Built to be extended.
