#!/usr/bin/env python3
import json
import sys
sys.path.insert(0, "/opt/astro")
from engine.corpus import get_corpus

d = json.load(open("/opt/astro/gemma_extractions/BPHS1_deep.json", encoding="utf-8"))
print("BPHS1 rules", d["n_rules_total"], "last", d["last_chunk_processed"], "total", d["n_chunks_total"], "complete", d["is_complete"])
print(get_corpus("/opt/astro/gemma_extractions").describe())
