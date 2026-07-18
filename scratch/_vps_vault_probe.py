#!/usr/bin/env python3
"""Run on VPS: list LLM providers (masked) and test in-process checkout."""
import os
import sys

ROOT = "/root/api-expense-manager"
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import config  # noqa: E402
import crypto  # noqa: E402
import models  # noqa: E402
import key_manager  # noqa: E402

models.init_db()
salt_hex = models.get_meta("vault_salt")
pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
if not pwd:
    print("FAIL: no master password in env")
    sys.exit(1)
crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
print("unlocked:", crypto.is_vault_unlocked())

for row in models.get_all_keys():
    if row["status"] != "active":
        continue
    p = row.get("provider", "")
    if p not in ("cerebras", "groq", "google", "nvidia", "sambanova", "gemini"):
        continue
    m = row.get("api_key_masked") or ""
    last4 = m[-4:] if len(m) >= 4 else "????"
    print(f"provider={p:10} model={row.get('model','')[:40]:40} last4=...{last4}")

svc = "93c4070a"  # nexus-metrix
for prov in ("cerebras", "groq", "google", "nvidia", "any"):
    r = key_manager.checkout_key(svc, prov)
    if r:
        k = r.get("api_key", "")
        print(f"checkout OK service=nexus-metrix provider={prov} model={r.get('model')} last4=...{k[-4:]}")
    else:
        print(f"checkout NO provider={prov}")
