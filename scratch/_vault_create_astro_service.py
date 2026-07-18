#!/usr/bin/env python3
"""Create or reuse 'astro' vault service; write bearer token to path (mode 600)."""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "/root/.astro_vault_token"
ROOT = "/root/api-expense-manager"
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import config  # noqa: E402
import crypto  # noqa: E402
import models  # noqa: E402

models.init_db()
salt_hex = models.get_meta("vault_salt")
pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
if not pwd:
    print("FAIL: VAULT_MASTER_PASSWORD required")
    sys.exit(1)
crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
if not crypto.is_vault_unlocked():
    print("FAIL: unlock")
    sys.exit(1)

for svc in models.get_all_services():
    if svc.get("name") == "astro":
        print(f"EXISTS astro id={svc['id']}")
        print("Create a new token in vault UI or delete and re-run.")
        sys.exit(0)

sid, token = models.add_service("astro", "Astro corpus deep extract", host="127.0.0.1")
# Assign LLM keys to astro service
keys = models.get_all_keys()
llm = [k for k in keys if k.get("provider") in ("cerebras", "groq", "google", "nvidia", "sambanova") and k["status"] == "active"]
for k in llm:
    models.assign_key_to_service(k["id"], sid)

with open(OUT, "w") as f:
    f.write(token.strip() + "\n")
os.chmod(OUT, 0o600)
print(f"WROTE {OUT} service_id={sid} token_last4=...{token.strip()[-4:]}")
