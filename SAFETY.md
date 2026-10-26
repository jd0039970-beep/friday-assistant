# Safety design: Sandbox ↔ Live mode

## Principles

1. **Default-deny.** Every tool that touches a real network, real disk encryption, or
   runs arbitrary generated code starts in `SANDBOX` scope. Nothing escalates itself.
2. **Explicit, typed, logged escalation.** Moving a specific target to `LIVE` requires
   the user to type an exact confirmation phrase naming that target. There is no voice
   shortcut for this — voice commands can never trigger Go Live, to prevent accidental
   or spoofed-audio escalation.
3. **Scoped, not global.** Going live authorizes one target (a path, a device, an IP/CIDR
   the user attests they own) for one session, with a time limit (default 30 min,
   re-confirm after). It never grants blanket "do anything live" permission.
4. **No autonomous target selection.** The agent can never choose what to scan/crack —
   the target is always supplied verbatim by the user and echoed back before escalation.
5. **Append-only audit log.** Every tool call (sandbox or live), every Go Live request
   (granted or denied), and every expiry is written to `~/.friday/audit.log` with a
   timestamp, the exact command, and the target. The log is never deleted by the agent.
6. **Visible state.** The desktop overlay shows a persistent red ring + "LIVE" badge
   any time live mode is active for any target, and reverts to the normal blue idle
   state the instant it expires or is revoked.
7. **No exploit authoring.** The security module is an *orchestrator* around tools the
   user installs and is responsible for themselves (nmap, hashcat, John, binwalk,
   Wireshark, etc.) via subprocess calls with argument allow-lists. It does not
   generate novel exploit code, shellcode, or malware, and it refuses targets that
   look like they're outside a private/lab IP range (RFC1918, `.local`, `localhost`)
   unless the user has separately attested ownership for that specific public target
   (e.g., their own VPS they're pentesting under a bug-bounty agreement) — this
   attestation is also logged.

## State machine

```
            ┌─────────────┐
            │   SANDBOX    │  (default, always available)
            │ docker, no   │
            │ network, cwd │
            │ = /sandbox   │
            └──────┬──────┘
                   │ user types:
                   │  "GO LIVE <target>"
                   ▼
            ┌──────────────────────┐
            │  CONFIRM (pending)   │  agent echoes target + risk back,
            │                      │  asks user to type the one-time token
            └──────────┬───────────┘
                      │ correct token typed
                      ▼
            ┌──────────────────────┐
            │     LIVE (scoped)    │  only the named target is allowed
            │   TTL = 30 min       │  tools run on host network/fs for that target
            │   red overlay on     │
            └──────────┬───────────┘
                      │ TTL expires / user says "stand down"
                      ▼
                   back to SANDBOX
```

## Hard lines

- F.R.I.D.A.Y never acquires elevated OS privileges (no sudo, no UAC elevation).
  If a command needs elevation, it prints the command for the user to run themselves.
- Voice path is structurally blocked from Go-Live (voice_sourced=True registry).
- Public IPs are refused unless explicitly attested.
- All security tools are allow-listed CLI wrappers only.
