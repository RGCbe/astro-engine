#!/usr/bin/env python3
"""Live quota summary per LLM provider (no full keys). Run on VPS with vault unlocked."""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

VAULT_ROOT = os.environ.get("VAULT_ROOT", "/root/api-expense-manager")
DB = os.environ.get("VAULT_DB", f"{VAULT_ROOT}/data/expense_manager.db")
TARGET_PROVIDERS = ("cerebras", "groq", "google", "nvidia", "sambanova")


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
    if not pwd or not salt_hex:
        raise RuntimeError("Set VAULT_MASTER_PASSWORD")
    crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
    if not crypto.is_vault_unlocked():
        raise RuntimeError("vault unlock failed")


def _classify(q: dict) -> str:
    status = q.get("status", "unknown")
    if status == "rate_limited":
        return "exhausted"
    if status == "error":
        err = (q.get("error") or "").lower()
        if "404" in err or "not found" in err or "model" in err:
            return "error_model"
        if "429" in err:
            return "exhausted"
        return "error"
    rpm_rem = int(q.get("rpm_remaining") or 0)
    rpd_rem = int(q.get("rpd_remaining") or 0)
    tpd_rem = int(q.get("tpd_remaining") or 0)
    day_pct = float(q.get("day_usage_pct") or 0)
    if rpm_rem == 0 and int(q.get("rpm_limit") or 0) > 0:
        return "exhausted"
    if rpd_rem == 0 and int(q.get("rpd_limit") or 0) > 0:
        return "exhausted"
    if tpd_rem == 0 and int(q.get("tpd_limit") or 0) > 0:
        return "exhausted"
    if day_pct >= 95:
        return "near_limit"
    if rpm_rem > 0 and int(q.get("rpm_limit") or 0) > 0:
        if rpm_rem <= max(2, int(q["rpm_limit"]) * 0.1):
            return "near_limit"
    if tpd_rem > 0 and int(q.get("tpd_limit") or 0) > 0:
        if tpd_rem <= max(1000, int(q["tpd_limit"]) * 0.1):
            return "near_limit"
    return "OK"


def main() -> None:
    _unlock()
    import crypto  # noqa: WPS433
    import models  # noqa: WPS433
    import quota_checker  # noqa: WPS433

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    keys_meta = {}
    for row in conn.execute(
        "SELECT id, provider, name, status, api_key_masked, model FROM api_keys "
        "WHERE status='active' ORDER BY provider, priority"
    ):
        masked = row["api_key_masked"] or ""
        last4 = masked[-4:] if len(masked) >= 4 else "????"
        keys_meta[row["id"]] = {
            "provider": row["provider"],
            "name": row["name"],
            "last4": last4,
            "model": row["model"],
        }

    keys_with_secrets = []
    for k in models.get_all_keys():
        if k["status"] != "active":
            continue
        if k["provider"] not in TARGET_PROVIDERS and k["provider"] not in ("gemini",):
            continue
        dec = crypto.decrypt_secret(k["api_key_encrypted"])
        if dec:
            k["api_key_decrypted"] = dec
            keys_with_secrets.append(k)

    quotas = quota_checker.check_all_quotas(keys_with_secrets)
    by_provider: dict[str, list] = {p: [] for p in TARGET_PROVIDERS}
    for q in quotas:
        kid = q.get("key_id", "")
        meta = keys_meta.get(kid, {})
        prov = meta.get("provider") or q.get("provider", "?")
        if prov == "gemini":
            prov = "google"
        if prov not in by_provider:
            continue
        row = {
            "provider": prov,
            "name": meta.get("name", "?"),
            "last4": meta.get("last4", "????"),
            "model": meta.get("model", "?"),
            "state": _classify(q),
            "status": q.get("status"),
            "rpm": f"{q.get('rpm_remaining','?')}/{q.get('rpm_limit','?')}",
            "rpd": f"{q.get('rpd_remaining','?')}/{q.get('rpd_limit','?')}",
            "tpd": f"{q.get('tpd_remaining','?')}/{q.get('tpd_limit','?')}",
            "day_pct": q.get("day_usage_pct", 0),
            "error": (q.get("error") or "")[:80],
        }
        by_provider[prov].append(row)

    print("provider     state          last4   model                    rpm        rpd        tpd")
    print("-" * 95)
    for prov in TARGET_PROVIDERS:
        rows = by_provider.get(prov) or []
        if not rows:
            print(f"{prov:12} NO_KEY")
            continue
        best = rows[0]
        for r in rows:
            if r["state"] == "OK":
                best = r
                break
        print(
            f"{best['provider']:12} {best['state']:14} ...{best['last4']:4}  "
            f"{(best['model'] or '?')[:24]:24}  {best['rpm']:10} {best['rpd']:10} {best['tpd']:10}"
        )
        if best.get("error") and best["state"] != "OK":
            print(f"             err: {best['error']}")


if __name__ == "__main__":
    main()
