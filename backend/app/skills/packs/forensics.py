"""Built-in forensics skill pack + executable runner."""
from __future__ import annotations

from typing import Callable

FORENSICS_SKILLS = {
    "identify_disk": {
        "description": "Identify a block device or image",
        "steps": ["file", "strings_sample"],
    },
    "extract_strings": {
        "description": "Pull readable strings",
        "steps": ["strings_full"],
    },
    "firmware_scan": {
        "description": "Binwalk analysis",
        "steps": ["binwalk"],
    },
    "hash_attack": {
        "description": "Wordlist attack (needs hash_file + wordlist)",
        "steps": ["hashcat"],
    },
    "full_lab_pass": {
        "description": "Identify → strings → binwalk → summary",
        "steps": ["file", "strings_sample", "binwalk", "summary"],
    },
}


def list_forensics_packs() -> str:
    lines = ["Forensics skill packs:"]
    for name, meta in FORENSICS_SKILLS.items():
        lines.append(f"  - {name}: {meta['description']}")
    return "\n".join(lines)


def run_forensics_pack(
    pack: str,
    target: str,
    *,
    run_file: Callable,
    run_strings: Callable,
    run_binwalk: Callable,
    run_hashcat: Callable | None = None,
    hash_file: str | None = None,
    wordlist: str | None = None,
) -> str:
    """Execute a named pack against target. Returns combined report."""
    if pack not in FORENSICS_SKILLS:
        return f"Unknown pack: {pack}. Use list_forensics_packs."

    steps = FORENSICS_SKILLS[pack]["steps"]
    report: list[str] = [f"=== Forensics pack: {pack} ===", f"Target: {target}", ""]

    for step in steps:
        report.append(f"--- {step} ---")
        try:
            if step == "file":
                report.append(str(run_file(target)))
            elif step == "strings_sample":
                report.append(str(run_strings(target, min_len=8))[:3000])
            elif step == "strings_full":
                report.append(str(run_strings(target, min_len=6))[:6000])
            elif step == "binwalk":
                report.append(str(run_binwalk(target, extract=False)))
            elif step == "hashcat":
                if not run_hashcat or not hash_file or not wordlist:
                    report.append("SKIP: need hash_file and wordlist")
                else:
                    report.append(str(run_hashcat(hash_file, wordlist)))
            elif step == "summary":
                report.append("Pack complete. Review findings above.")
            else:
                report.append(f"Unknown step {step}")
        except Exception as e:
            report.append(f"ERROR in {step}: {e}")
        report.append("")

    return "\n".join(report)
