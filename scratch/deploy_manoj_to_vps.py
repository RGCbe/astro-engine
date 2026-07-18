#!/usr/bin/env python3
"""Upload Manoj chart, life facts, prediction engine, and reports to VPS."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VPS_HOST = "root@46.28.44.225"
VPS_DIR = "/opt/astro"
ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "charts/manoj_chart.json",
    "charts/manoj_life_facts.json",
    "engine/prediction_confirm.py",
    "engine/engine_topic_confirm.py",
    "engine/per_book_predictions.py",
    "engine/lagna_filter.py",
    "scratch/manoj_confirmed_predictions.py",
    "scratch/manoj_engine_confirmed.py",
    "scratch/manoj_per_book_predictions.py",
    "docs/MANOJ_PREDICTION_SAVE_CHECKPOINT.md",
]

REPORT_DIR = ROOT / "reports" / "jun 2026" / "2026-06-02" / "report" / "manoj"


def upload(local_rel: str) -> bool:
    local = ROOT / local_rel.replace("/", "\\") if "\\" in str(ROOT) else ROOT / local_rel
    if not local.exists():
        print(f"[SKIP] missing {local_rel}")
        return True
    remote = f"{VPS_DIR}/{local_rel.replace(chr(92), '/')}"
    remote_dir = str(Path(remote).parent).replace("\\", "/")
    subprocess.run(["ssh", VPS_HOST, f"mkdir -p {remote_dir}"], capture_output=True)
    r = subprocess.run(["scp", str(local), f"{VPS_HOST}:{remote}"], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"[{'OK' if ok else 'FAIL'}] {local_rel}")
    if not ok and r.stderr:
        print(r.stderr.strip())
    return ok


def upload_reports() -> bool:
    if not REPORT_DIR.exists():
        print("[SKIP] report dir missing")
        return True
    remote_base = f"{VPS_DIR}/reports/jun 2026/2026-06-02/report/manoj"
    subprocess.run(["ssh", VPS_HOST, f"mkdir -p '{remote_base}'"], capture_output=True)
    ok_all = True
    for f in REPORT_DIR.glob("*.md"):
        r = subprocess.run(
            ["scp", str(f), f"{VPS_HOST}:{remote_base}/{f.name}"],
            capture_output=True,
            text=True,
        )
        print(f"[{'OK' if r.returncode == 0 else 'FAIL'}] report/{f.name}")
        ok_all = ok_all and r.returncode == 0
    return ok_all


def main() -> None:
    print(f"Deploying Manoj data to {VPS_HOST}:{VPS_DIR}")
    ok = all(upload(f) for f in FILES)
    ok = upload_reports() and ok
    if ok:
        cmd = (
            f"cd {VPS_DIR} && ./venv/bin/python scratch/manoj_confirmed_predictions.py "
            f"&& ./venv/bin/python scratch/manoj_engine_confirmed.py"
        )
        r = subprocess.run(
            ["ssh", VPS_HOST, cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print("--- VPS regenerate reports ---")
        print(r.stdout or r.stderr)
        subprocess.run(["ssh", VPS_HOST, "pm2 restart astro-engine"], capture_output=True)
        print("pm2 restart astro-engine (done)")
    print("DONE" if ok else "SOME UPLOADS FAILED")


if __name__ == "__main__":
    main()
