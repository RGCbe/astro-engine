import sys
import time
from pathlib import Path
from openai import OpenAI

vault_root = "/root/api-expense-manager"
sys.path.insert(0, vault_root)

import models
import crypto

def main():
    # 1. Load password and unlock vault
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
        print("[-] Error: vault credentials not found")
        sys.exit(1)

    crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
    if not crypto.is_vault_unlocked():
        print("[-] Error: unlock failed")
        sys.exit(1)

    # 2. Get NVIDIA key
    api_key = None
    base_url = "https://integrate.api.nvidia.com/v1"
    for k in models.get_all_keys():
        if k.get("provider") == "nvidia" and k.get("status") == "active":
            api_key = crypto.decrypt_secret(k["api_key_encrypted"])
            if k.get("base_url"):
                base_url = k.get("base_url")
            break
            
    if not api_key:
        print("[-] Error: Active NVIDIA key not found in vault")
        sys.exit(1)
        
    print(f"[+] Found NVIDIA API key. Base URL: {base_url}")
    
    # 3. Test OpenAI client with a Vision model
    # We will try Meta Llama 3.2 11B Vision Instruct
    model_name = "meta/llama-3.2-11b-vision-instruct"
    print(f"[*] Testing NVIDIA NIM Vision call to model: {model_name}...")
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    try:
        # We send a text-only call first to verify key access, but using the vision model name
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Return the word 'HELLO_NVIDIA' and nothing else."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        print("[OK] Success!")
        print("Response:", resp.choices[0].message.content.strip())
    except Exception as e:
        print(f"[-] Vision call failed: {e}")
        
if __name__ == "__main__":
    main()
