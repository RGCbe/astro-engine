#!/bin/bash
# On VPS: wait for Bhrigu, ensure engine restart, write continue flag.
set -euo pipefail
cd /opt/astro
LOG=/opt/astro/logs/after_bhrigu.log
echo "=== wait Bhrigu $(date -Iseconds) ===" | tee -a "$LOG"
while true; do
  line=$(./venv/bin/python scratch/_book_progress.py 2>/dev/null | grep Bhrigu_Samhita || true)
  echo "$(date -Iseconds) $line" >> "$LOG"
  complete=$(./venv/bin/python -c "import json; d=json.load(open('gemma_extractions/Bhrigu_Samhita_deep.json')); print(d.get('is_complete'))" 2>/dev/null || echo false)
  if [ "$complete" = "True" ] || echo "$line" | grep -q '219/219.*complete=True'; then
    echo "Bhrigu complete � pm2 restart astro-engine" | tee -a "$LOG"
    pm2 restart astro-engine >> "$LOG" 2>&1
    ./venv/bin/python scratch/_corpus_stats_once.py >> "$LOG" 2>&1 || true
    echo "CONTINUE_B_READY $(date -Iseconds)" > /opt/astro/scratch/BHIGRU_DONE_CONTINUE_B.flag
    break
  fi
  sleep 120
done
