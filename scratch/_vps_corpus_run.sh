#!/bin/bash
set -euo pipefail
cd /opt/astro

echo "=== DIRS ==="
ls -la _workbench/_deep_extract.py scratch/_vault_checkout_test.py

echo "=== BASELINE CORPUS ==="
./venv/bin/python -c 'from engine.corpus import get_corpus; c=get_corpus("gemma_extractions"); print(c.describe())'

echo "=== INCOMPLETE BOOKS ==="
for f in gemma_extractions/*_deep.json; do
  ./venv/bin/python -c "
import json, sys
d=json.load(open('$f'))
book=d.get('book','?')
last=d.get('last_chunk_processed',-1)
total=d.get('n_chunks_total',0)
done=last+1
pct=100*(total-done)/total if total else 0
print(f'{book}: {done}/{total} missing={pct:.1f}% complete={d.get(\"is_complete\",False)}')
"
done
