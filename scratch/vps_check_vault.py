import sys
from pathlib import Path

vault_root = "/root/api-expense-manager"
sys.path.insert(0, vault_root)

import models
import crypto

# Load password
env_file = Path(vault_root) / ".env"
pwd = ""
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("VAULT_MASTER_PASSWORD="):
            pwd = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

models.init_db()
salt_hex = models.get_meta("vault_salt")
if not pwd or not salt_hex:
    print("Error: vault credentials not found")
    sys.exit(1)

crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
if not crypto.is_vault_unlocked():
    print("Error: unlock failed")
    sys.exit(1)

print("Vault unlocked successfully!")
print("Active keys in database:")
for k in models.get_all_keys():
    print(f"ID: {k.get('id')} | Provider: {k.get('provider')} | Model: {k.get('model')} | Status: {k.get('status')}")
