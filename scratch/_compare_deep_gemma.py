import json
from pathlib import Path

pairs = [
    "Jataka_Bharanam",
    "Bhrigu_Samhita",
    "BPHS1",
    "KP_Reader_3_Predictive",
    "Sarvartha_Chintamani",
    "Surya_Siddhanta",
]
g = Path("gemma_extractions")
for b in pairs:
    deep = g / f"{b}_deep.json"
    gemma = g / f"{b}_gemma.json"
    d = json.loads(deep.read_text(encoding="utf-8", errors="replace"))
    dr = len(d.get("rules", []))
    gr = 0
    if gemma.exists():
        gd = json.loads(gemma.read_text(encoding="utf-8", errors="replace"))
        gr = len(gd.get("rules", []))
    ic = d.get("is_complete")
    chunks = f"{d.get('last_chunk_processed')}/{d.get('n_chunks_total')}"
    print(f"{b}: deep={dr} gemma={gr} complete={ic} chunks={chunks}")
