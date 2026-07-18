import subprocess
import os
import sys

# Configure stdout for utf-8
sys.stdout.reconfigure(encoding="utf-8")

VPS_HOST = "root@46.28.44.225"
VPS_DIR = "/opt/astro"

def upload_file(local_path, remote_path):
    print(f"[+] Uploading: {local_path} -> {VPS_HOST}:{remote_path} ... ", end="", flush=True)
    try:
        # Create remote directory
        remote_dir = os.path.dirname(remote_path)
        subprocess.run(["ssh", VPS_HOST, f"mkdir -p {remote_dir}"], capture_output=True)
        
        # SCP
        r = subprocess.run(["scp", local_path, f"{VPS_HOST}:{remote_path}"], capture_output=True, text=True)
        if r.returncode == 0:
            print(" [OK]")
            return True
        else:
            print(f" [FAIL] ({r.stderr.strip()})")
            return False
    except Exception as e:
        print(f" [ERROR] ({e})")
        return False

def run_remote_command(cmd, desc):
    print(f"[+] Running remote command: {desc} ... ")
    try:
        r = subprocess.run(["ssh", VPS_HOST, f"cd {VPS_DIR} && {cmd}"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("--- REMOTE OUTPUT ---")
        print(r.stdout)
        if r.stderr.strip():
            print("--- REMOTE ERRORS ---")
            print(r.stderr)
        print("---------------------")
        return r.returncode == 0
    except Exception as e:
        print(f" [ERROR] ({e})")
        return False

def main():
    print("=" * 80)
    print("           VPS COMPATIBILITY DEPLOYMENT AND RELOAD")
    print("=" * 80)
    
    # Files to upload
    files_to_upload = [
        ("engine/kuta.py", "engine/kuta.py"),
        ("engine/iching_engine.py", "engine/iching_engine.py"),
        ("engine/extended_compatibility.py", "engine/extended_compatibility.py"),
        ("engine/numerology_match.py", "engine/numerology_match.py"),
        ("scratch/generate_separate_reports.py", "scratch/generate_separate_reports.py"),
        ("scratch/match_viveka.py", "scratch/match_viveka.py")
    ]
    
    upload_success = True
    for local, remote in files_to_upload:
        if not upload_file(local, f"{VPS_DIR}/{remote}"):
            upload_success = False
            
    if not upload_success:
        print("Error: File upload failed. Aborting deployment.")
        return

    # Reload PM2 process
    reload_cmd = "pm2 reload astro-engine"
    reload_success = run_remote_command(reload_cmd, "PM2 astro-engine Hot-Reload")
    
    if reload_success:
        print("\n=========================================================================")
        print(" SUCCESS: Compatibility Engines & Reports Successfully Deployed and Reloaded on VPS!")
        print("=========================================================================")
    else:
        print("\nWarning: PM2 reload returned non-zero status. Please check process logs manually.")

if __name__ == "__main__":
    main()
