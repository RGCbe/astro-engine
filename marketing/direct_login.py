#!/usr/bin/env python3
"""AstroMystic AI — Direct Instagram Authenticator"""
import sys
import json
from instagrapi import Client

if len(sys.argv) < 4:
    print("Usage: python direct_login.py <username> <password> <session_file_path>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
session_file = sys.argv[3]

cl = Client()
cl.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")

try:
    print(f"[+] Logging in programmatically as: {username} ...")
    cl.login(username, password)
    
    settings = cl.get_settings()
    with open(session_file, "w") as f:
        json.dump(settings, f, indent=2)
        
    print("[SUCCESS] Session saved successfully!")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Direct Login Failed: {e}")
    sys.exit(1)
