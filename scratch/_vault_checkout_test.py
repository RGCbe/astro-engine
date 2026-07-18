#!/usr/bin/env python3
"""Test vault unlock + checkout (run on VPS from api-expense-manager dir)."""
import os
import sys
from pathlib import Path

ROOT = "/root/api-expense-manager"
sys.path.insert(0, ROOT)
os.chdir(ROOT)

env_file = Path(ROOT) / ".env"
if env_file.exists() and not os.environ.get("VAULT_MASTER_PASSWORD"):
    for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("VAULT_MASTER_PASSWORD="):
            os.environ["VAULT_MASTER_PASSWORD"] = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

import config  # noqa: E402
import crypto  # noqa: E402
import models  # noqa: E402
import key_manager  # noqa: E402

models.init_db()
salt_hex = models.get_meta("vault_salt")
if not salt_hex:
    print("FAIL: no vault salt")
    sys.exit(1)
salt = bytes.fromhex(salt_hex)
pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
if not pwd:
    print("FAIL: no VAULT_MASTER_PASSWORD")
    sys.exit(1)
crypto.unlock_vault(pwd, salt)
print("unlocked:", crypto.is_vault_unlocked())

# Try checkout for each LLM provider used by deep extract
providers = ["cerebras", "groq", "google", "nvidia", "gemini", "any"]
service_id = sys.argv[1] if len(sys.argv) > 1 else "93c4070a"  # nexus-metrix default
for prov in providers:
    try:
        r = key_manager.checkout_key(service_id, prov)
        if r:
            k = r.get("api_key", "")
            tail = k[-4:] if len(k) >= 4 else "????"
            print(f"OK checkout provider={prov} model={r.get('model')} last4=...{tail}")
        else:
            print(f"NO_KEY provider={prov}")
    except Exception as e:
        print(f"ERR provider={prov}: {e}")
