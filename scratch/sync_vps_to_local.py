import os
import subprocess
from pathlib import Path

VPS_HOST = "root@46.28.44.225"
VPS_BOOKS_DIR = "/opt/astro/Books"
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

def run_scp_download(remote_path, local_path):
    print(f"[+] Downloading: {remote_path} -> {local_path} ... ", end="", flush=True)
    
    # Ensure local directory exists
    Path(local_path).parent.mkdir(exist_ok=True, parents=True)
    
    r = subprocess.run(["scp"] + SSH_OPTS + [f"{VPS_HOST}:{remote_path}", str(local_path)], capture_output=True, text=True)
    if r.returncode == 0:
        print("[OK]")
        return True
    else:
        print(f"[FAIL] ({r.stderr.strip()})")
        return False

def main():
    print("=" * 80)
    print("      VPS TO LOCAL SYNCHRONIZER (DOWNLOADER)")
    print("=" * 80)
    
    # 1. Catalog local files
    local_books = {f.name: f for f in Path("books").iterdir() if f.is_file()} if Path("books").exists() else {}
    if not local_books:
        # Fallback to uppercase "Books" folder if lowercase doesn't exist
        local_books = {f.name: f for f in Path("Books").iterdir() if f.is_file()} if Path("Books").exists() else {}
    local_gemma = {f.name: f for f in Path("gemma_extractions").iterdir() if f.is_file() and f.suffix == ".json"} if Path("gemma_extractions").exists() else {}
    
    # 2. Gather VPS files
    print("[+] Querying VPS file lists...")
    vps_books_raw = run_ssh(f"find {VPS_BOOKS_DIR} -maxdepth 1 -type f -exec stat -c '%n %s' {{}} + 2>/dev/null")
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
    vps_gemma = parse_vps(vps_gemma_raw)
    
    downloads = []
    
    # --- Check /books ---
    # Determine the local books target directory name
    local_books_dir = Path("books") if Path("books").exists() else Path("Books")
    
    for name, info in vps_books.items():
        # Only sync text/PDF files
        if not (name.endswith(".txt") or name.endswith(".pdf")):
            continue
        l_path = local_books_dir / name
        if name not in local_books:
            downloads.append((info["path"], l_path))
        else:
            lsize = l_path.stat().st_size
            vsize = info["size"]
            if vsize > lsize:
                downloads.append((info["path"], l_path))
                
    # --- Check /gemma_extractions ---
    local_gemma_dir = Path("gemma_extractions")
    for name, info in vps_gemma.items():
        if not name.endswith(".json"):
            continue
        # Skip backup folder files
        l_path = local_gemma_dir / name
        if name not in local_gemma:
            downloads.append((info["path"], l_path))
        else:
            lsize = l_path.stat().st_size
            vsize = info["size"]
            if vsize > lsize:
                downloads.append((info["path"], l_path))
                
    print(f"\n[+] Detected {len(downloads)} files to download from VPS.")
    
    # Perform Downloads
    success_count = 0
    for idx, (r_path, l_path) in enumerate(downloads):
        print(f"[{idx+1}/{len(downloads)}] ", end="")
        if run_scp_download(r_path, l_path):
            success_count += 1
            
    print(f"\n[+] Download process finished: {success_count}/{len(downloads)} files synced successfully.")

if __name__ == "__main__":
    main()
