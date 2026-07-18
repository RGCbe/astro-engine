#!/usr/bin/env python3
"""Fix cerebras model in vault DB when probe returns 404. No key output."""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

VAULT_ROOT = os.environ.get("VAULT_ROOT", "/root/api-expense-manager")
DB = f"{VAULT_ROOT}/data/expense_manager.db"
FALLBACK_MODELS = ("llama-3.3-70b", "llama3.1-8b", "llama3.1-70b")


def _unlock() -> None:
    env_file = Path(VAULT_ROOT) / ".env"
    if env_file.exists() and not os.environ.get("VAULT_MASTER_PASSWORD"):
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("VAULT_MASTER_PASSWORD="):
                os.environ["VAULT_MASTER_PASSWORD"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    sys.path.insert(0, VAULT_ROOT)
    os.chdir(VAULT_ROOT)
    import config  # noqa: WPS433
    import crypto  # noqa: WPS433
    import models  # noqa: WPS433

    models.init_db()
    salt_hex = models.get_meta("vault_salt")
    pwd = config.VAULT_MASTER_PASSWORD or os.environ.get("VAULT_MASTER_PASSWORD", "")
    crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))


def _list_cerebras_models(api_key: str) -> list[str]:
    import requests

    r = requests.get(
        "https://api.cerebras.ai/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=15,
    )
    if r.status_code != 200:
        return []
    data = r.json()
    ids = []
    for item in data.get("data", data if isinstance(data, list) else []):
        mid = item.get("id") if isinstance(item, dict) else str(item)
        if mid:
            ids.append(mid)
    return ids


def main() -> None:
    _unlock()
    import crypto  # noqa: WPS433
    import models  # noqa: WPS433
    import quota_checker  # noqa: WPS433

    keys = [k for k in models.get_all_keys() if k["provider"] == "cerebras" and k["status"] == "active"]
    if not keys:
        print("no active cerebras key")
        return
    k = keys[0]
    api_key = crypto.decrypt_secret(k["api_key_encrypted"])
    if not api_key:
        print("decrypt failed")
        return
    masked = (k.get("api_key_masked") or "")[-4:]
    current = k.get("model") or ""
    q = quota_checker.check_quota(k["id"], api_key, k["base_url"], current, "cerebras")
    err = (q.error or "").lower()
    if q.status == "healthy":
        print(f"cerebras OK model={current} last4=...{masked}")
        return
    if "404" not in err and "not found" not in err and q.status != "error":
        print(f"cerebras skip fix status={q.status} model={current} err={q.error[:60]}")
        return
    available = _list_cerebras_models(api_key)
    pick = None
    for cand in FALLBACK_MODELS:
        if cand in available:
            pick = cand
            break
    if not pick and available:
        pick = available[0]
    if not pick:
        print(f"cannot fix: no models listed; was {current}")
        return
    if pick == current:
        print(f"already {current} but still error: {q.error[:80]}")
        return
    conn = sqlite3.connect(DB)
    conn.execute(
        "UPDATE api_keys SET model=?, updated_at=datetime('now') WHERE id=?",
        (pick, k["id"]),
    )
    conn.commit()
    print(f"cerebras model {current} -> {pick} (last4=...{masked})")


if __name__ == "__main__":
    main()
