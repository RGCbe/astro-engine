#!/bin/bash
set -euo pipefail
cd /opt/astro

# Ensure vault deps in astro venv (required for --vault-direct)
./venv/bin/pip install -q argon2-cffi requests openai 2>/dev/null || true

# Load vault password silently
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  if [ -f /root/api-expense-manager/.env ]; then
    export VAULT_MASTER_PASSWORD=$(grep -E '^VAULT_MASTER_PASSWORD=' /root/api-expense-manager/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  fi
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  VAULT_MASTER_PASSWORD=$(pm2 env api-vault 2>/dev/null | grep -E '^VAULT_MASTER_PASSWORD:' | head -1 | sed 's/^VAULT_MASTER_PASSWORD: //')
  export VAULT_MASTER_PASSWORD
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  echo "FAIL: no VAULT_MASTER_PASSWORD"
  exit 1
fi

# Wait if another deep_extract is already running
while pgrep -f '_deep_extract.py' >/dev/null 2>&1; do
  echo "waiting for existing deep_extract process..."
  sleep 30
done

LOG=/opt/astro/logs/corpus_resume_$(date +%Y%m%d_%H%M%S).log
mkdir -p /opt/astro/logs
exec > >(tee -a "$LOG") 2>&1

echo "=== CORPUS RESUME START $(date -Iseconds) ==="
echo "log: $LOG"

echo "=== BASELINE ==="
./venv/bin/python -c 'from engine.corpus import get_corpus; c=get_corpus("gemma_extractions"); print(c.describe())'

BOOKS=(
  Sarvartha_Chintamani
  BPHS1
  KP_Reader_3_Predictive
  Bhrigu_Samhita
  Jataka_Bharanam
)

for book in "${BOOKS[@]}"; do
  echo ""
  echo "=== BOOK: $book $(date -Iseconds) ==="
  # Skip if already complete
  complete=$(./venv/bin/python -c "
import json
d=json.load(open('gemma_extractions/${book}_deep.json'))
print('yes' if d.get('is_complete') else 'no')
" 2>/dev/null || echo "missing")
  if [ "$complete" = "yes" ]; then
    echo "SKIP $book already complete"
    continue
  fi
  if [ "$complete" = "missing" ]; then
    echo "SKIP $book no deep json"
    continue
  fi
  before=$(./venv/bin/python -c "
import json
d=json.load(open('gemma_extractions/${book}_deep.json'))
print(d.get('last_chunk_processed',-1)+1, d.get('n_chunks_total',0))
")
  echo "before chunks: $before"
  if ! ./venv/bin/python _workbench/_deep_extract.py --book "$book" --resume --vault-direct; then
    echo "ERROR: $book extraction failed (see log); continuing to next book"
  fi
  after=$(./venv/bin/python -c "
import json
d=json.load(open('gemma_extractions/${book}_deep.json'))
print(d.get('last_chunk_processed',-1)+1, d.get('n_chunks_total',0), 'complete='+str(d.get('is_complete',False)))
")
  echo "after chunks: $after"
done

echo ""
echo "=== FINAL CORPUS ==="
./venv/bin/python -c 'from engine.corpus import get_corpus; c=get_corpus("gemma_extractions"); print(c.describe())'

echo ""
echo "=== INCOMPLETE SUMMARY ==="
for f in gemma_extractions/*_deep.json; do
  ./venv/bin/python -c "
import json
d=json.load(open('$f'))
if not d.get('is_complete'):
  book=d.get('book','?')
  last=d.get('last_chunk_processed',-1)
  total=d.get('n_chunks_total',0)
  done=last+1
  pct=100*(total-done)/total if total else 0
  print(f'INCOMPLETE {book}: {done}/{total} missing={pct:.1f}%')
"
done

echo "=== RESTART astro-engine ==="
pm2 restart astro-engine
sleep 5
pm2 logs astro-engine --lines 15 --nostream || true

echo "=== DONE $(date -Iseconds) ==="
