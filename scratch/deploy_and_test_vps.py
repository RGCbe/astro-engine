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
    print("           VPS DEPLOYMENT AND TESTING SUITE (PHASE 7 INTEGRATION)")
    print("=" * 80)
    
    # 1. Upload engine files
    files_to_upload = [
        ("engine/evaluator.py", "engine/evaluator.py"),
        ("runtime/kp_paddhati.py", "runtime/kp_paddhati.py"),
        ("engine/jaimini_full.py", "engine/jaimini_full.py"),
        ("engine/nadi_jyotish.py", "engine/nadi_jyotish.py"),
        ("engine/tajik.py", "engine/tajik.py"),
        ("engine/western_engine.py", "engine/western_engine.py"),
        ("engine/chinese_engine.py", "engine/chinese_engine.py"),
        ("engine/mayan_engine.py", "engine/mayan_engine.py"),
        ("engine/numerology_engine.py", "engine/numerology_engine.py"),
        ("scratch/test_global_engines.py", "scratch/test_global_engines.py"),
        ("scratch/test_numerology.py", "scratch/test_numerology.py"),
        ("scratch/optimize_astro_numerology.py", "scratch/optimize_astro_numerology.py"),
        ("scratch/astro_numerology_weights.json", "scratch/astro_numerology_weights.json"),
        ("main.py", "main.py")
    ]
    
    upload_success = True
    for local, remote in files_to_upload:
        if not upload_file(local, f"{VPS_DIR}/{remote}"):
            upload_success = False
            
    if not upload_success:
        print("Error: File upload failed. Aborting deployment.")
        return

    # 2. Run integration tests on VPS
    # We run test_full_integration.py on VPS inside its environment
    test_cmd = "/opt/astro/venv/bin/python test_full_integration.py"
    test_success = run_remote_command(test_cmd, "Vedic Engine Integration Test Suite")
    
    if not test_success:
        print("Error: Remote integration tests failed. Aborting hot-reload.")
        return

    # Run GAC tests on VPS
    gac_test_cmd = "/opt/astro/venv/bin/python scratch/test_global_engines.py"
    gac_test_success = run_remote_command(gac_test_cmd, "GAC Engine Integration Test Suite")
    
    if not gac_test_success:
        print("Error: Remote GAC integration tests failed. Aborting hot-reload.")
        return

    # Run Numerology tests on VPS
    num_test_cmd = "/opt/astro/venv/bin/python scratch/test_numerology.py"
    num_test_success = run_remote_command(num_test_cmd, "Numerology Engine Integration Test Suite")
    
    if not num_test_success:
        print("Error: Remote Numerology integration tests failed. Aborting hot-reload.")
        return

    # Run Conjoined Optimizer on VPS
    opt_test_cmd = "/opt/astro/venv/bin/python scratch/optimize_astro_numerology.py"
    opt_test_success = run_remote_command(opt_test_cmd, "Conjoined Astro-Numerology Optimization Execution")
    
    if not opt_test_success:
        print("Error: Remote Conjoined Astro-Numerology optimization failed. Aborting hot-reload.")
        return

    # 3. Reload PM2 process
    reload_cmd = "pm2 reload astro-engine"
    reload_success = run_remote_command(reload_cmd, "PM2 astro-engine Hot-Reload")
    
    if reload_success:
        print("\n=========================================================================")
        print(" SUCCESS: Vedic Engine Successfully Deployed, Tested, and Reloaded on VPS!")
        print("=========================================================================")
    else:
        print("\nWarning: PM2 reload returned non-zero status. Please check process logs manually.")

if __name__ == "__main__":
    main()
