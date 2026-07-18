#!/bin/bash
set -euo pipefail
cd /opt/astro

if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  if [ -f /root/api-expense-manager/.env ]; then
    export VAULT_MASTER_PASSWORD=$(grep -E '^VAULT_MASTER_PASSWORD=' /root/api-expense-manager/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  fi
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  VAULT_MASTER_PASSWORD=$(pm2 env api-vault 2>/dev/null | grep -E '^VAULT_MASTER_PASSWORD:' | head -1 | sed 's/^VAULT_MASTER_PASSWORD: //' || true)
  export VAULT_MASTER_PASSWORD
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  echo "FAIL: no VAULT_MASTER_PASSWORD"
  exit 1
fi

LOG=/opt/astro/logs/corpus_quota_resume_$(date +%Y%m%d_%H%M%S).log
mkdir -p /opt/astro/logs
exec > >(tee -a "$LOG") 2>&1

VAULT_PY="${VAULT_PY:-python3}"
ASTRO_PY="${ASTRO_PY:-/opt/astro/venv/bin/python}"

echo "=== QUOTA CHECK $(date -Iseconds) ==="
"$VAULT_PY" /tmp/_vault_quota_summary.py || true
echo "=== CEREBRAS MODEL FIX ==="
"$VAULT_PY" /tmp/_fix_cerebras_model.py || true
echo "=== QUOTA AFTER FIX ==="
"$VAULT_PY" /tmp/_vault_quota_summary.py || true

echo ""
echo "=== BASELINE CORPUS ==="
./venv/bin/python /tmp/_corpus_stats_once.py 2>/dev/null || ./venv/bin/python -c 'from engine.corpus import get_corpus; print(get_corpus("gemma_extractions").describe())'

BOOKS=(
  Sarvartha_Chintamani
  KP_Reader_3_Predictive
  Bhrigu_Samhita
  Jataka_Bharanam
)

for book in "${BOOKS[@]}"; do
  echo ""
  echo "=== BOOK: $book $(date -Iseconds) ==="
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
print(d.get('last_chunk_processed',-1)+1, '/', d.get('n_chunks_total',0))
")
  echo "before chunks done: $before"
  if ! "$ASTRO_PY" _workbench/_deep_extract.py --book "$book" --resume --vault-direct; then
    echo "STOPPED: $book extraction error (rate limit or failure)"
    break
  fi
  after=$(./venv/bin/python -c "
import json
d=json.load(open('gemma_extractions/${book}_deep.json'))
print('after', d.get('last_chunk_processed',-1)+1, '/', d.get('n_chunks_total',0), 'complete='+str(d.get('is_complete',False)))
")
  echo "$after"
done

echo ""
echo "=== FINAL ==="
./venv/bin/python /tmp/_corpus_stats_once.py 2>/dev/null || true
python3 scratch/_inventory_incomplete.py 2>/dev/null || true

echo "=== RESTART astro-engine ==="
pm2 restart astro-engine
sleep 5
pm2 logs astro-engine --lines 10 --nostream || true
echo "log: $LOG"
