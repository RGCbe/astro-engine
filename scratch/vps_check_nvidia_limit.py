import sys
import requests
from pathlib import Path

vault_root = "/root/api-expense-manager"
sys.path.insert(0, vault_root)

import models
import crypto

def main():
    # 1. Load password
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
        print("Error: credentials not found")
        sys.exit(1)

    crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
    if not crypto.is_vault_unlocked():
        print("Error: unlock failed")
        sys.exit(1)

    key = None
    for k in models.get_all_keys():
        if k.get("provider") == "nvidia" and k.get("status") == "active":
            key = crypto.decrypt_secret(k["api_key_encrypted"])
            break

    if not key:
        print("No active NVIDIA key found")
        sys.exit(0)

    print("Checking NVIDIA NIM quota/rate limit headers...")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta/llama-3.2-11b-vision-instruct",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5
    }
    
    r = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", json=payload, headers=headers)
    print("Response Status Code:", r.status_code)
    print("\nRelevant Headers:")
    found = False
    for h, v in r.headers.items():
        hl = h.lower()
        if any(term in hl for term in ("rate", "limit", "credit", "quota", "remaining", "reset")):
            print(f"  {h}: {v}")
            found = True
    if not found:
        print("  No rate limit/quota headers returned by NVIDIA integrate API.")

if __name__ == "__main__":
    main()
