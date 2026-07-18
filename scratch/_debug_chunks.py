#!/usr/bin/env python3
import sys
sys.path.insert(0, "/opt/astro")
from pathlib import Path
from _workbench._deep_extract import _smart_chunks, _calibrate_target_chars

t = Path("/opt/astro/Books/BPHS1_extracted.txt").read_text(encoding="utf-8", errors="replace")
print("text_len", len(t))
tc = _calibrate_target_chars(t, 203)
c = list(_smart_chunks(t, tc))
print("tc", tc, "n_chunks", len(c))
