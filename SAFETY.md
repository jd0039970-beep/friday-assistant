# Safety design

## What is restricted

1. **Default = sandbox**  
   Security tools run inside Docker with `--network none` unless Live is granted for that specific target.

2. **Voice cannot escalate**  
   Workshop Mode, Go-Live, and trusted-target changes require typed input.

3. **No privilege escalation by the agent**  
   Friday never runs `sudo` / UAC elevation herself. She prints the command if elevation is needed.

4. **Append-only audit log**  
   Every tool call and every Live grant is written to `~/.friday/audit.log`.

## What is NOT restricted (by design)

- **Local paths, block devices, encrypted drives**  
  `/dev/sdX`, `\\.\PhysicalDriveN`, mounted volumes, image files — all treated as local lab targets.

- **Private IP ranges and localhost**  
  Always eligible for Live.

- **`unrestricted_local: true` (default in config)**  
  For wired-only or air-gapped machines (no WiFi/BT). Any target can be taken Live without an ownership attestation step.  
  Set to `false` only if this machine has a route to the public internet and you want the extra prompt.

## Workshop Mode

Typed once:
```
enable workshop mode
add trusted target /dev/sdb
add trusted target 192.168.1.50
```
Trusted targets then auto-Live when you ask. No repeated confirmation spam for your own hardware.

## Intent

This is built for legitimate ownership cases: old encrypted MOD drives, lab laptops, CTF images, home network gear you control. The sandbox still exists so a bad tool invocation does not automatically touch the host; Live is explicit and logged.
