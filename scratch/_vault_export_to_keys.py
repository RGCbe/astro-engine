#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export LLM keys from unlocked vault to _workbench/.keys/ (run on VPS).

Usage:
  cd /root/api-expense-manager && VAULT_MASTER_PASSWORD=... python3 /tmp/_vault_export_to_keys.py /opt/astro/_workbench/.keys

Writes: cerebras.key, groq.key, nvidia.key, google.key (providers present in vault).
Does not print full keys - only ...last4 per file.
"""
import os
import sys

VAULT_ROOT = "/root/api-expense-manager"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/opt/astro/_workbench/.keys"
PROVIDERS = ("cerebras", "groq", "google", "nvidia", "gemini", "sambanova")

sys.path.insert(0, VAULT_ROOT)
os.chdir(VAULT_ROOT)

import config  # noqa: E402
import crypto  # noqa: E402
import models  # noqa: E402

models.init_db()
salt_hex = models.get_meta("vault_salt")
if not salt_hex:
    print("FAIL: vault not initialized")
    sys.exit(1)
pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
if not pwd:
    print("FAIL: set VAULT_MASTER_PASSWORD")
    sys.exit(1)
crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
if not crypto.is_vault_unlocked():
    print("FAIL: unlock failed")
    sys.exit(1)

os.makedirs(OUT, mode=0o700, exist_ok=True)
keys = models.get_all_keys()
by_prov = {}
for k in keys:
    if k["status"] != "active":
        continue
    p = (k.get("provider") or "").lower()
    if p in PROVIDERS and p not in by_prov:
        plain = crypto.decrypt_secret(k["api_key_encrypted"])
        if not plain:
            print(f"SKIP {p}: decrypt failed")
            continue
        path = os.path.join(OUT, f"{p}.key")
        with open(path, "w") as f:
            f.write(plain.strip() + "\n")
        by_prov[p] = path
        print(f"WROTE {path} last4=...{plain.strip()[-4:]}")

print("done:", sorted(by_prov.keys()))
