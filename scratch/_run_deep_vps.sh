#!/bin/bash
set -e
cd /opt/astro
export VAULT_MASTER_PASSWORD="$(python3 -c "import subprocess,re; o=subprocess.check_output(['pm2','env','api-vault'],text=True,stderr=subprocess.DEVNULL); m=re.search(r'VAULT_MASTER_PASSWORD:\s*(\S+)',o); print(m.group(1) if m else '')")"
if [ -z "$VAULT_MASTER_PASSWORD" ]; then
  echo "FAIL: could not read VAULT_MASTER_PASSWORD from pm2 env api-vault"
  exit 1
fi
echo "vault pwd loaded (not printed)"
python3 _workbench/_deep_extract.py --book BPHS1 --resume --vault-direct "$@"
