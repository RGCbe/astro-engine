#!/bin/bash
set -euo pipefail
cd /root/api-expense-manager

# Load master password from pm2 env or .env without printing it
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  if [ -f .env ]; then
    export VAULT_MASTER_PASSWORD=$(grep -E '^VAULT_MASTER_PASSWORD=' .env | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  fi
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  VAULT_MASTER_PASSWORD=$(pm2 env api-vault 2>/dev/null | grep -E '^VAULT_MASTER_PASSWORD:' | head -1 | sed 's/^VAULT_MASTER_PASSWORD: //')
  export VAULT_MASTER_PASSWORD
fi
if [ -z "${VAULT_MASTER_PASSWORD:-}" ]; then
  echo "FAIL: could not load VAULT_MASTER_PASSWORD"
  exit 1
fi
echo "vault password: loaded (not shown)"

echo "=== VAULT PROBE ==="
python3 /opt/astro/scratch/_vps_vault_probe.py

echo "=== CHECKOUT TEST ==="
python3 /opt/astro/scratch/_vault_checkout_test.py

echo "=== ASTRO SERVICE ==="
if [ ! -f /root/.astro_vault_token ]; then
  python3 /opt/astro/scratch/_vault_create_astro_service.py /root/.astro_vault_token || true
else
  echo "token file exists: /root/.astro_vault_token (mode $(stat -c %a /root/.astro_vault_token))"
fi
