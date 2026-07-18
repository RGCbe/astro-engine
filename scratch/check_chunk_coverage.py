import json
from pathlib import Path
import sys
sys.path.insert(0, '.')
from engine.corpus import EXCLUDED_BOOKS

print("=" * 105)
print("  CHUNK COVERAGE & EXTRACTION COMPLETENESS AUDIT (FIXED)")
print("=" * 105)
print(f"{'BOOK':<35} {'RULES':>5} {'CHUNKS':>6} {'ACTIVE_CH':>9} {'MAX_RULE_CH':>11} {'COVERAGE':>8} {'FORMAT':>7}")
print("-" * 105)

for f in sorted(Path('gemma_extractions').iterdir()):
    if f.is_file() and f.suffix == '.json' and not f.name.startswith('_'):
        name = f.stem
        if name in EXCLUDED_BOOKS:
            continue
        try:
            raw_data = json.loads(f.read_text(encoding='utf-8'))
            
            if isinstance(raw_data, list):
                rules = raw_data
                n_chunks_total = 0 # No chunk total info
                fmt = "LIST"
            else:
                rules = raw_data.get('rules', raw_data.get('extractions', []))
                n_chunks_total = raw_data.get('n_chunks_total', 0)
                fmt = "DICT"
                
            rule_count = len(rules)
            
            # Find which chunks have rules
            chunks_with_rules = set()
            max_chunk = -1
            for r in rules:
                if isinstance(r, dict):
                    ch = r.get('_chunk_idx', r.get('chunk_idx', r.get('chunk', -1)))
                    if ch != -1:
                        chunks_with_rules.add(ch)
                        max_chunk = max(max_chunk, ch)
            
            # If LIST and we have chunk indices, we can infer n_chunks_total as max_chunk + 1
            inferred_chunks = n_chunks_total
            if inferred_chunks == 0 and max_chunk != -1:
                inferred_chunks = max_chunk + 1
                
            active_chunks = len(chunks_with_rules)
            coverage = (active_chunks / inferred_chunks * 100) if inferred_chunks > 0 else 0
            
            base = name.replace('_deep', '').replace('_gemma', '')
            cov_str = f"{coverage:.1f}%" if inferred_chunks > 0 else "N/A"
            print(f"{base:<35} {rule_count:>5} {inferred_chunks:>6} {active_chunks:>9} {max_chunk:>11} {cov_str:>8} {fmt:>7}")
        except Exception as e:
            print(f"Error {name}: {e}")
