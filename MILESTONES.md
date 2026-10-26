# Status & next steps

## Done
- [x] Agent brain (Qwen2.5-7B + tool calling)
- [x] Sandbox ↔ Live + audit log
- [x] Workshop Mode + trusted targets (no permission spam on lab gear)
- [x] unrestricted_local for offline / wired-only machines
- [x] PC control (mouse, keyboard, files, clipboard, processes)
- [x] Vision (screenshot + OCR, webcam)
- [x] Web (Playwright)
- [x] Voice stubs (faster-whisper + Piper en_GB-alba)
- [x] Holographic FRIDAY HUD
- [x] Self-skill system (create → test → promote)
- [x] Forensics tools she drives: nmap, hashcat, john, binwalk, file, strings
- [x] Allow-listed shell (`run_command`)
- [x] Tool router (doesn't dump every tool every turn)
- [x] ETA in HUD

## Next (priority order)

### 1. Desktop shell (highest impact)
- Tauri app wrapping the HUD
- Always-on-top overlay / system tray
- Global push-to-talk hotkey
- Start with OS so she feels like a real installed assistant

### 2. Voice completion
- Wire push-to-talk end-to-end
- Optional "Hey Friday" wake word
- Interruptible TTS

### 3. Stronger forensics workflows
- Pre-built skill packs: "image this disk", "extract hashes", "run wordlist attack"
- Mount helpers for encrypted volumes (she prints the cryptsetup/mount commands if root needed)
- Progress / ETA for long hashcat jobs

### 4. Proactive mode
- Optional background watchers (disk plugged in, process crash, network change)
- She initiates: "Boss, new block device at /dev/sdc — want me to image it?"

### 5. Polish
- One-click installer
- Better persona few-shots
- Optional higher-quality TTS (Kokoro) path
