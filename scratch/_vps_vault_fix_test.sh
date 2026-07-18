#!/bin/bash
set -euo pipefail

echo "=== argon2 install ==="
/opt/astro/venv/bin/pip install argon2-cffi requests openai 2>&1 | tail -3

echo "=== api-vault status ==="
pm2 show api-vault 2>/dev/null | grep -E 'status|port|pid' || pm2 list | grep api-vault
curl -s -m 5 http://127.0.0.1:5055/health 2>&1 || curl -s -m 5 http://127.0.0.1:5055/ 2>&1 | head -c 200 || echo "vault HTTP unreachable"

echo "=== token file ==="
if [ -f /root/.astro_vault_token ]; then
  echo "exists mode=$(stat -c %a /root/.astro_vault_token) len=$(wc -c < /root/.astro_vault_token)"
else
  echo "MISSING"
fi

echo "=== astro services ==="
export VAULT_MASTER_PASSWORD=$(grep -E '^VAULT_MASTER_PASSWORD=' /root/api-expense-manager/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
python3 /opt/astro/scratch/_vault_create_astro_service.py 2>&1 || true

echo "=== direct unlock test ==="
python3 /opt/astro/scratch/_vault_checkout_test.py 2>&1 | head -10

echo "=== single chunk with venv vault-direct ==="
export VAULT_MASTER_PASSWORD
cd /opt/astro
./venv/bin/python _workbench/_deep_extract.py --book Sarvartha_Chintamani --resume --vault-direct --max-chunks 1 2>&1
