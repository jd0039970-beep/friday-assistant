"""Built-in forensics skill pack.

These are ready-made workflows Friday can run with one instruction from you.
"""
from __future__ import annotations

FORENSICS_SKILLS = {
    "identify_disk": {
        "description": "Identify a block device or image (file type, size, partition hint)",
        "steps": [
            "run_file on the path",
            "run_command 'lsblk -f' or equivalent",
            "run_strings with min_len 8 (sample)",
            "summarise findings for the user",
        ],
    },
    "extract_strings": {
        "description": "Pull readable strings from a binary/drive image",
        "steps": [
            "run_strings on the path",
            "optionally write interesting hits to a file via write_file",
        ],
    },
    "firmware_scan": {
        "description": "Binwalk analysis of firmware / disk image",
        "steps": [
            "run_binwalk path",
            "if interesting, run_binwalk with extract=True inside sandbox",
        ],
    },
    "hash_attack": {
        "description": "Wordlist attack on a hash file",
        "steps": [
            "confirm hash file + wordlist paths",
            "run_hashcat or run_john",
            "report cracked / not cracked",
        ],
    },
    "full_lab_pass": {
        "description": "End-to-end: identify → strings → binwalk → suggest hash path",
        "steps": [
            "enable workshop + trust target if needed",
            "identify_disk",
            "extract_strings",
            "firmware_scan",
            "propose next attack if hashes found",
        ],
    },
}


def list_forensics_packs() -> str:
    lines = ["Forensics skill packs:"]
    for name, meta in FORENSICS_SKILLS.items():
        lines.append(f"  - {name}: {meta['description']}")
    return "\n".join(lines)
