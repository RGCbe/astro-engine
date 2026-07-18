import sqlite3
c = sqlite3.connect("/root/api-expense-manager/data/vault.db")
print("tables:", [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")])
for row in c.execute("SELECT provider, status FROM keys LIMIT 20"):
    print(row)
