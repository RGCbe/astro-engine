#!/bin/bash
# Run on VPS: proof resume BPHS1 (4 chunks) with vault-direct, no key files.
set -euo pipefail
if [ ! -f /root/.astro_vault_token ]; then
  export VAULT_MASTER_PASSWORD
  VAULT_MASTER_PASSWORD=$(pm2 env 1 2>/dev/null | awk -F': ' '/^VAULT_MASTER_PASSWORD:/{sub(/^VAULT_MASTER_PASSWORD: /,""); print; exit}')
  if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
    echo "FAIL: could not load VAULT_MASTER_PASSWORD from pm2 api-vault"
    exit 1
  fi
fi
cd /opt/astro
PY=/opt/astro/venv/bin/python3
if [ ! -x "$PY" ]; then PY=python3; fi
if [ ! -f /root/.astro_vault_token ]; then
  /usr/bin/python3 /tmp/_vault_create_astro_service.py /root/.astro_vault_token
fi
export VAULT_URL=https://127.0.0.1:5055
export VAULT_TOKEN
VAULT_TOKEN=$(cat /root/.astro_vault_token)
export VAULT_SERVICE=astro
$PY -c "from engine.corpus import get_corpus; print('BEFORE', get_corpus('gemma_extractions').describe())"
$PY _workbench/_deep_extract_resume.py --book BPHS1 --resume --max-chunks 4
$PY -c "from engine.corpus import get_corpus; print('AFTER', get_corpus('gemma_extractions').describe())"
