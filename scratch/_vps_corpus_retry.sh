#!/bin/bash
# Re-run only incomplete target books until all complete or max passes reached
set -euo pipefail
cd /opt/astro

PAUSE_FLAG="/opt/astro/scratch/EXTRACTION_PAUSED.flag"
if [ -f "$PAUSE_FLAG" ]; then
  echo "EXTRACTION PAUSED ($(cat "$PAUSE_FLAG")). Remove flag to resume. Exiting."
  exit 0
fi

./venv/bin/pip install -q argon2-cffi requests openai 2>/dev/null || true

if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  export VAULT_MASTER_PASSWORD=$(grep -E '^VAULT_MASTER_PASSWORD=' /root/api-expense-manager/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
fi

MAX_PASSES=${1:-5}
BOOKS=(KP_Reader_3_Predictive Bhrigu_Samhita Jataka_Bharanam Sarvartha_Chintamani)

for pass in $(seq 1 "$MAX_PASSES"); do
  if [ -f "$PAUSE_FLAG" ]; then
    echo "EXTRACTION PAUSED during pass $pass. Exiting."
    exit 0
  fi
  echo "=== PASS $pass/$MAX_PASSES $(date -Iseconds) ==="
  while pgrep -f '_deep_extract.py' >/dev/null 2>&1; do
    echo "waiting for deep_extract..."
    sleep 60
  done
  any_incomplete=0
  for book in "${BOOKS[@]}"; do
    complete=$(./venv/bin/python -c "import json; d=json.load(open('gemma_extractions/${book}_deep.json')); print('yes' if d.get('is_complete') else 'no')" 2>/dev/null || echo missing)
    [ "$complete" = "yes" ] || [ "$complete" = "missing" ] && continue
    any_incomplete=1
    echo "=== RESUME $book ==="
    ./venv/bin/python _workbench/_deep_extract.py --book "$book" --resume --vault-direct || echo "WARN: $book pass failed, will retry"
    sleep 30
  done
  [ "$any_incomplete" = "0" ] && echo "ALL COMPLETE" && break
  echo "cooldown 120s before next pass..."
  sleep 120
done

echo "=== FINAL STATUS ==="
bash /opt/astro/scratch/_vps_status.sh
./venv/bin/python -c 'from engine.corpus import get_corpus; print(get_corpus("gemma_extractions").describe())'
pm2 restart astro-engine
echo "DONE $(date -Iseconds)"
