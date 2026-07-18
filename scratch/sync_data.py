import json
import subprocess
from pathlib import Path
import os
import sys

# Configure stdout for utf-8
sys.stdout.reconfigure(encoding="utf-8")

LOCAL_DIR = Path("f:/Atro").resolve()
VPS_HOST = "root@46.28.44.225"
VPS_DIR = "/opt/astro"

def run_command_cmd(cmd_list):
    try:
        r = subprocess.run(cmd_list, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode == 0, r.stdout, r.stderr
    except Exception as e:
        return False, "", str(e)

def download_file(rel_path):
    local_path = LOCAL_DIR / rel_path
    local_path.parent.mkdir(parents=True, exist_ok=True)
    vps_path = f"{VPS_HOST}:{VPS_DIR}/{rel_path}"
    print(f"Downloading: {rel_path} ...", end="", flush=True)
    
    # Run scp
    success, _, err = run_command_cmd(["scp", vps_path, str(local_path)])
    if success:
        print(" [OK]")
        return True
    else:
        print(f" [FAIL] ({err.strip()})")
        return False

def upload_file(rel_path):
    local_path = LOCAL_DIR / rel_path
    vps_path = f"{VPS_HOST}:{VPS_DIR}/{rel_path}"
    
    # Ensure remote directory exists
    remote_parent = os.path.dirname(f"{VPS_DIR}/{rel_path}")
    subprocess.run(["ssh", VPS_HOST, f"mkdir -p {remote_parent}"])
    
    print(f"Uploading: {rel_path} ...", end="", flush=True)
    success, _, err = run_command_cmd(["scp", str(local_path), vps_path])
    if success:
        print(" [OK]")
        return True
    else:
        print(f" [FAIL] ({err.strip()})")
        return False

def main():
    local_scan_path = LOCAL_DIR / "scratch/local_scan.json"
    vps_scan_path = LOCAL_DIR / "scratch/vps_scan.json"
    
    if not local_scan_path.exists() or not vps_scan_path.exists():
        print("Error: local_scan.json or vps_scan.json not found in scratch/")
        return
        
    local_scan = json.loads(local_scan_path.read_text(encoding="utf-8-sig"))
    vps_scan = json.loads(vps_scan_path.read_text(encoding="utf-8-sig"))
    
    # Categories to download (VPS -> Local)
    # 1. Any file in gemma_extractions/*.json (our structured extractions & master index)
    # 2. Any file in Books/*_extracted.txt (the OCR raw text files)
    files_to_download = []
    for rel_path, info in vps_scan.items():
        # Check if file is gemma extraction or extracted text
        is_extractions = rel_path.startswith("gemma_extractions/") and rel_path.endswith(".json")
        is_extracted_text = rel_path.startswith("Books/") and rel_path.endswith("_extracted.txt")
        
        if is_extractions or is_extracted_text:
            if rel_path not in local_scan or local_scan[rel_path]["md5"] != info["md5"]:
                # If local is larger for deep files, let's preserve it unless remote is even larger
                if rel_path in local_scan:
                    local_size = local_scan[rel_path]["size"]
                    vps_size = info["size"]
                    if local_size > vps_size and "deep" in rel_path:
                        print(f"Preserving local deeper file: {rel_path} ({local_size:,} vs VPS {vps_size:,} bytes)")
                        continue
                files_to_download.append(rel_path)
                
    # Categories to upload (Local -> VPS)
    # 1. Code files (.py files in engine/ or runtime/, or root py files)
    # 2. Config files (.json in logic_base/)
    # 3. Web files in frontend/
    files_to_upload = []
    for rel_path, info in local_scan.items():
        is_code = (rel_path.startswith("engine/") or rel_path.startswith("runtime/") or "/" not in rel_path) and rel_path.endswith(".py")
        is_logic = rel_path.startswith("logic_base/") and rel_path.endswith(".json")
        is_web = rel_path.startswith("frontend/")
        
        if is_code or is_logic or is_web:
            # Skip scratch files
            if rel_path.startswith("scratch/"):
                continue
            if rel_path not in vps_scan or vps_scan[rel_path]["md5"] != info["md5"]:
                # For code files, local is the absolute source of truth
                files_to_upload.append(rel_path)
                
    print("=" * 70)
    print(f"Pending alignment plan:")
    print(f"  Files to download (VPS -> Local) : {len(files_to_download)}")
    print(f"  Files to upload (Local -> VPS)   : {len(files_to_upload)}")
    print("=" * 70)
    
    downloaded_count = 0
    for p in files_to_download:
        if download_file(p):
            downloaded_count += 1
            
    uploaded_count = 0
    for p in files_to_upload:
        if upload_file(p):
            uploaded_count += 1
            
    print("=" * 70)
    print(f"Sync complete! Downloaded {downloaded_count}/{len(files_to_download)} files. Uploaded {uploaded_count}/{len(files_to_upload)} files.")
    print("=" * 70)

if __name__ == "__main__":
    main()
