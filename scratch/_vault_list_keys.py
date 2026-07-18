#!/usr/bin/env python3
"""List vault providers from expense_manager.db (no full keys)."""
import sqlite3
import sys

db = sys.argv[1] if len(sys.argv) > 1 else "/root/api-expense-manager/data/expense_manager.db"
c = sqlite3.connect(db)
c.row_factory = sqlite3.Row
print("=== api_keys ===")
for row in c.execute(
    "SELECT provider, name, status, api_key_masked, priority "
    "FROM api_keys ORDER BY provider, priority"
):
    masked = row["api_key_masked"] or ""
    last4 = masked[-4:] if len(masked) >= 4 else masked
    print(
        f"{row['provider']:12} {row['name']:24} status={row['status']:8} "
        f"last4=...{last4} prio={row['priority']}"
    )
print("\n=== services ===")
for row in c.execute("SELECT id, name FROM services ORDER BY name"):
    print(f"{row['id']}  {row['name']}")
print("\n=== vault_meta ===")
for row in c.execute("SELECT key, value FROM vault_meta"):
    v = row["value"]
    if len(str(v)) > 40:
        v = str(v)[:20] + "..."
    print(f"{row['key']}: {v}")
