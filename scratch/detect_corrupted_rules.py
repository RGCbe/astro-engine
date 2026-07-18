import json
import string
from pathlib import Path
import sys
sys.path.insert(0, '.')
from engine.corpus import EXCLUDED_BOOKS

def is_corrupted(text):
    if not text:
        return False
    # Count printable vs non-printable characters
    printable = set(string.printable)
    unprintable_count = sum(1 for c in text if c not in printable)
    # If more than 15% of characters are non-printable, or if we see control/null chars or \ufffd
    ratio = unprintable_count / len(text) if len(text) > 0 else 0
    if ratio > 0.10:
        return True
    if '\u0000' in text or '\ufffd' in text or '\u001a' in text:
        # Check if it's mostly non-english
        return True
    return False

print("=" * 80)
print("  CORRUPTED RULE TEXT DETECTION")
print("=" * 80)

corrupted_files = []
total_corrupted_rules = 0
total_active_rules = 0

for f in sorted(Path('gemma_extractions').iterdir()):
    if f.is_file() and f.suffix == '.json' and not f.name.startswith('_'):
        name = f.stem
        if name in EXCLUDED_BOOKS:
            continue
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            rules = data if isinstance(data, list) else data.get('rules', data.get('extractions', []))
            if not isinstance(rules, list):
                continue
            
            file_corrupted_rules = 0
            for r in rules:
                total_active_rules += 1
                if isinstance(r, dict):
                    txt = r.get('rule_text', r.get('text', ''))
                    if is_corrupted(txt):
                        file_corrupted_rules += 1
                        total_corrupted_rules += 1
            
            if file_corrupted_rules > 0:
                pct = (file_corrupted_rules / len(rules)) * 100
                corrupted_files.append((name, len(rules), file_corrupted_rules, pct))
        except Exception as e:
            print(f"Error reading {name}: {e}")

corrupted_files.sort(key=lambda x: -x[2])
for name, total, corr, pct in corrupted_files:
    print(f"  {name:<40} Total Rules: {total:>5}  Corrupted Rules: {corr:>5} ({pct:>5.1f}%)")

print("\n" + "=" * 80)
print(f"Total active rules: {total_active_rules}")
print(f"Total corrupted rules: {total_corrupted_rules} ({total_corrupted_rules/total_active_rules*100:.1f}%)")
print(f"Total files with corruption: {len(corrupted_files)}")
print("=" * 80)
