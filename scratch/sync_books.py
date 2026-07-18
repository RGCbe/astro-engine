import os
import subprocess
from pathlib import Path

VPS_HOST = "root@46.28.44.225"
VPS_BOOKS_DIR = "/opt/astro/Books"
VPS_KNOWLEDGE_DIR = "/opt/astro/knowledge"
VPS_GEMMA_DIR = "/opt/astro/gemma_extractions"

def run_ssh(cmd):
    full_cmd = ["ssh", VPS_HOST, cmd]
    r = subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout

def run_scp_download(remote_path, local_path):
    print(f"Downloading: {VPS_HOST}:{remote_path} -> {local_path}")
    r = subprocess.run(["scp", f"{VPS_HOST}:{remote_path}", str(local_path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERROR] Download failed: {r.stderr.strip()}")
    return r.returncode == 0

def run_scp_upload(local_path, remote_path):
    print(f"Uploading: {local_path} -> {VPS_HOST}:{remote_path}")
    
    # Create remote directory structure if needed
    remote_dir = os.path.dirname(remote_path)
    run_ssh(f"mkdir -p {remote_dir}")
    
    r = subprocess.run(["scp", str(local_path), f"{VPS_HOST}:{remote_path}"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERROR] Upload failed: {r.stderr.strip()}")
    return r.returncode == 0

def main():
    print("=" * 80)
    print("        ASTRO VEDIC ENGINE — BI-DIRECTIONAL BOOK SYNCHRONIZER")
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
    
    def parse_vps(raw_text, subdir):
        vps_dict = {}
        for line in raw_text.splitlines():
            parts = line.rsplit(maxsplit=1)
            if len(parts) == 2:
                path, size = parts[0], int(parts[1])
                name = Path(path).name
                if subdir == "knowledge" and not (name.endswith(".pdf") or "_raw" in name):
                    continue
                if subdir == "gemma_extractions" and (not name.endswith(".json") or name.startswith("_")):
                    continue
                vps_dict[name] = {"path": path, "size": size}
        return vps_dict
        
    vps_books = parse_vps(vps_books_raw, "books")
    vps_knowledge = parse_vps(vps_knowledge_raw, "knowledge")
    vps_gemma = parse_vps(vps_gemma_raw, "gemma_extractions")
    
    downloads = []
    uploads = []
    
    # --- PROCESS /books AND /opt/astro/Books ---
    # VPS Only -> Download
    for name, info in vps_books.items():
        if name not in local_books:
            downloads.append((info["path"], Path("books") / name))
            
    # Local Only -> Upload
    for name, path in local_books.items():
        if name not in vps_books:
            uploads.append((path, f"{VPS_BOOKS_DIR}/{name}"))
            
    # --- PROCESS /knowledge AND /opt/astro/knowledge ---
    # VPS Only -> Download
    for name, info in vps_knowledge.items():
        if name not in local_knowledge:
            downloads.append((info["path"], Path("knowledge") / name))
            
    # Local Only -> Upload
    for name, path in local_knowledge.items():
        if name not in vps_knowledge:
            uploads.append((path, f"{VPS_KNOWLEDGE_DIR}/{name}"))

    # --- PROCESS /gemma_extractions AND /opt/astro/gemma_extractions ---
    # VPS Only -> Download
    for name, info in vps_gemma.items():
        if name not in local_gemma:
            downloads.append((info["path"], Path("gemma_extractions") / name))
            
    # Local Only -> Upload
    for name, path in local_gemma.items():
        if name not in vps_gemma:
            uploads.append((path, f"{VPS_GEMMA_DIR}/{name}"))
            
    # Mismatch check (e.g. Bhrigu_Samhita_deep.json)
    for name, path in local_gemma.items():
        if name in vps_gemma:
            lsize = path.stat().st_size
            vsize = vps_gemma[name]["size"]
            if lsize != vsize:
                if vsize > lsize:
                    # Pull larger file from VPS
                    print(f"[!] {name} size mismatch: Local={lsize} vs VPS={vsize}. Choosing larger VPS version.")
                    downloads.append((vps_gemma[name]["path"], path))
                else:
                    # Push larger file to VPS
                    print(f"[!] {name} size mismatch: Local={lsize} vs VPS={vsize}. Choosing larger Local version.")
                    uploads.append((path, vps_gemma[name]["path"]))

    print(f"\n[+] Synchronization Plan:")
    print(f"  - Files to download from VPS: {len(downloads)}")
    print(f"  - Files to upload to VPS:   {len(uploads)}")
    
    # 3. Create folders locally if they do not exist
    Path("books").mkdir(exist_ok=True)
    Path("knowledge").mkdir(exist_ok=True)
    Path("gemma_extractions").mkdir(exist_ok=True)
    
    # 4. Perform Downloads
    download_success_count = 0
    if downloads:
        print("\n[+] Starting Downloads...")
        for r_path, l_path in downloads:
            if run_scp_download(r_path, l_path):
                download_success_count += 1
                
    # 5. Perform Uploads
    upload_success_count = 0
    if uploads:
        print("\n[+] Starting Uploads...")
        for l_path, r_path in uploads:
            if run_scp_upload(l_path, r_path):
                upload_success_count += 1
                
    # 6. Verify sync
    print("\n" + "=" * 80)
    print("                    SYNCHRONIZATION COMPLETED")
    print("=" * 80)
    print(f"Downloads: {download_success_count}/{len(downloads)} succeeded.")
    print(f"Uploads:   {upload_success_count}/{len(uploads)} succeeded.")
    
    # Regenerate local master dedup if needed, or check corpus on both sides!
    print("[+] Done!")

if __name__ == "__main__":
    main()
