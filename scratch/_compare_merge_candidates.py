"""Compare rules in _deep vs excluded _gemma for incomplete books."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GEMMA = Path(__file__).resolve().parent.parent / "gemma_extractions"

INCOMPLETE = [
    "Jataka_Bharanam",
    "Bhrigu_Samhita",
    "BPHS1",
    "KP_Reader_3_Predictive",
    "Sarvartha_Chintamani",
    "Surya_Siddhanta",
]


def collect_gemma_rules(data):
    rules = list(data.get("rules") or [])
    for chunk in data.get("chunks") or []:
        for r in chunk.get("predictive_rules") or []:
            rules.append(
                {
                    "english_translation": (r.get("effect") or "").strip(),
                    "original_text": (r.get("trigger") or "").strip(),
                    "_chunk_idx": chunk.get("chunk_num"),
                    "_extractor": chunk.get("_provider", "gemma_chunk"),
                }
            )
        for y in chunk.get("yogas_named") or []:
            rules.append(
                {
                    "english_translation": (y.get("effects") or "").strip(),
                    "original_text": (y.get("yoga_name") or "").strip(),
                    "_extractor": "gemma_yoga",
                }
            )
    return [r for r in rules if (r.get("english_translation") or "").strip()]


for book in INCOMPLETE:
    deep_p = GEMMA / f"{book}_deep.json"
    gemma_p = GEMMA / f"{book}_gemma.json"
    deep = json.loads(deep_p.read_text(encoding="utf-8", errors="replace"))
    dr = deep.get("rules") or []
    deep_texts = {(r.get("english_translation") or "").strip().lower()[:80] for r in dr}
    grules = []
    if gemma_p.exists():
        gd = json.loads(gemma_p.read_text(encoding="utf-8", errors="replace"))
        grules = collect_gemma_rules(gd)
    new = [
        r
        for r in grules
        if (r.get("english_translation") or "").strip().lower()[:80] not in deep_texts
    ]
    print(
        f"{book}: deep={len(dr)} gemma={len(grules)} "
        f"gemma_not_in_deep={len(new)} complete={deep.get('is_complete')}"
    )
