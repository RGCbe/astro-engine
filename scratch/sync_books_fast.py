import os
import subprocess
from pathlib import Path

VPS_HOST = "root@46.28.44.225"
VPS_BOOKS_DIR = "/opt/astro/Books"
VPS_KNOWLEDGE_DIR = "/opt/astro/knowledge"
VPS_GEMMA_DIR = "/opt/astro/gemma_extractions"

SSH_OPTS = [
    "-o", "ConnectTimeout=10",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=3"
]

def run_ssh(cmd):
    full_cmd = ["ssh"] + SSH_OPTS + [VPS_HOST, cmd]
    r = subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout

def run_scp_upload(local_path, remote_path):
    print(f"[+] Uploading: {local_path} -> {remote_path} ... ", end="", flush=True)
    
    # Create remote directory structure if needed
    remote_dir = os.path.dirname(remote_path)
    run_ssh(f"mkdir -p {remote_dir}")
    
    r = subprocess.run(["scp"] + SSH_OPTS + [str(local_path), f"{VPS_HOST}:{remote_path}"], capture_output=True, text=True)
    if r.returncode == 0:
        print("[OK]")
        return True
    else:
        print(f"[FAIL] ({r.stderr.strip()})")
        return False

def main():
    print("=" * 80)
    print("      ROBUST RESUMABLE SYNCHRONIZER (WITH KEEPALIVES & TIMEOUTS)")
    print("=" * 80)
    
    # 1. Catalog local files
    local_books = {f.name: f for f in Path("books").iterdir() if f.is_file()} if Path("books").exists() else {}
    local_knowledge = {f.name: f for f in Path("knowledge").iterdir() if f.is_file() and (f.suffix == ".pdf" or "_raw" in f.name)}
    local_gemma = {f.name: f for f in Path("gemma_extractions").iterdir() if f.is_file() and f.suffix == ".json" and not f.name.startswith("_")}
    
    # 2. Gather VPS files
    print("[+] Querying VPS file lists...")
    vps_books_raw = run_ssh(f"find {VPS_BOOKS_DIR} -maxdepth 1 -type f -exec stat -c '%n %s' {{}} + 2>/dev/null")
    vps_knowledge_raw = run_ssh(f"find {VPS_KNOWLEDGE_DIR} -maxdepth 1 -type f -exec stat -c '%n %s' {{}} + 2>/dev/null")
    vps_gemma_raw = run_ssh(f"find {VPS_GEMMA_DIR} -maxdepth 1 -type f -exec stat -c '%n %s' {{}} + 2>/dev/null")
    
    def parse_vps(raw_text):
        vps_dict = {}
        for line in raw_text.splitlines():
            parts = line.rsplit(maxsplit=1)
            if len(parts) == 2:
                path, size = parts[0], int(parts[1])
                vps_dict[Path(path).name] = {"path": path, "size": size}
        return vps_dict
        
    vps_books = parse_vps(vps_books_raw)
    vps_knowledge = parse_vps(vps_knowledge_raw)
    vps_gemma = parse_vps(vps_gemma_raw)
    
    uploads = []
    
    # --- Check /books ---
    for name, path in local_books.items():
        if name not in vps_books:
            uploads.append((path, f"{VPS_BOOKS_DIR}/{name}"))
        else:
            lsize = path.stat().st_size
            vsize = vps_books[name]["size"]
            if lsize > vsize:
                uploads.append((path, f"{VPS_BOOKS_DIR}/{name}"))
                
    # --- Check /knowledge ---
    for name, path in local_knowledge.items():
        if name not in vps_knowledge:
            uploads.append((path, f"{VPS_KNOWLEDGE_DIR}/{name}"))
        else:
            lsize = path.stat().st_size
            vsize = vps_knowledge[name]["size"]
            if lsize > vsize:
                uploads.append((path, f"{VPS_KNOWLEDGE_DIR}/{name}"))
                
    # --- Check /gemma_extractions ---
    for name, path in local_gemma.items():
        if name not in vps_gemma:
            uploads.append((path, f"{VPS_GEMMA_DIR}/{name}"))
        else:
            lsize = path.stat().st_size
            vsize = vps_gemma[name]["size"]
            if lsize > vsize:
                uploads.append((path, f"{VPS_GEMMA_DIR}/{name}"))
                
    print(f"\n[+] Detected {len(uploads)} files to upload to VPS.")
    
    # Perform Uploads
    success_count = 0
    for idx, (l_path, r_path) in enumerate(uploads):
        print(f"[{idx+1}/{len(uploads)}] ", end="")
        if run_scp_upload(l_path, r_path):
            success_count += 1
            
    print(f"\n[+] Upload process finished: {success_count}/{len(uploads)} files synced successfully.")

if __name__ == "__main__":
    main()
