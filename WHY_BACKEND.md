# Why is there a "backend"?

Friday is a **local** AI. Nothing about the backend is the public internet.

| Piece | Role | Where it runs |
|-------|------|----------------|
| **Ollama** | The LLM (Qwen) | Your PC |
| **Backend** (`python -m app.main`) | Brain: tools, memory, voice, plans | Your PC only (`127.0.0.1`) |
| **HUD / app window** | The face you talk to | Your PC |

Without the backend process you only have a model chat with **no** mouse/keyboard, files, forensics, workshop mode, or memory.

`127.0.0.1` = this machine only. Not the web.

The launcher starts the backend **hidden** and opens a **frameless app window** (Edge/Chrome `--app` mode) so it feels like one app, not a website.
