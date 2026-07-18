import os
import subprocess
import json
from pathlib import Path

def run_ssh(cmd):
    full_cmd = ["ssh", "root@46.28.44.225", cmd]
    r = subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8")
    return r.stdout

def main():
    # 1. Gather Local Books (/books, /knowledge, /gemma_extractions)
    local_books = {}
    
    # Check /books
    books_dir = Path("books")
    if books_dir.exists():
        for f in books_dir.iterdir():
            if f.is_file():
                local_books[f.name] = {"local_size": f.stat().st_size, "vps_size": None, "dir": "books"}
                
    # Check /knowledge
    knowledge_dir = Path("knowledge")
    if knowledge_dir.exists():
        for f in knowledge_dir.iterdir():
            if f.is_file() and (f.suffix == ".pdf" or "_raw" in f.name):
                local_books[f.name] = {"local_size": f.stat().st_size, "vps_size": None, "dir": "knowledge"}
                
    # Check /gemma_extractions
    gemma_dir = Path("gemma_extractions")
    if gemma_dir.exists():
        for f in gemma_dir.iterdir():
            if f.is_file() and f.suffix == ".json" and not f.name.startswith("_"):
                local_books[f.name] = {"local_size": f.stat().st_size, "vps_size": None, "dir": "gemma_extractions"}

    # 2. Gather VPS Books (/opt/astro/Books, /opt/astro/knowledge, /opt/astro/gemma_extractions)
    print("Fetching file list and sizes from VPS...")
    vps_books_raw = run_ssh("find /opt/astro/Books -maxdepth 1 -type f -exec stat -c '%n %s' {} + 2>/dev/null")
    vps_knowledge_raw = run_ssh("find /opt/astro/knowledge -maxdepth 1 -type f -exec stat -c '%n %s' {} + 2>/dev/null")
    vps_gemma_raw = run_ssh("find /opt/astro/gemma_extractions -maxdepth 1 -type f -exec stat -c '%n %s' {} + 2>/dev/null")
    
    vps_books = {}
    
    def parse_vps_lines(raw_text, subdir):
        for line in raw_text.splitlines():
            parts = line.rsplit(maxsplit=1)
            if len(parts) == 2:
                path, size = parts[0], int(parts[1])
                name = Path(path).name
                if subdir == "knowledge" and not (name.endswith(".pdf") or "_raw" in name):
                    continue
                if subdir == "gemma_extractions" and (not name.endswith(".json") or name.startswith("_")):
                    continue
                vps_books[name] = {"size": size, "dir": subdir}
                
    parse_vps_lines(vps_books_raw, "books")
    parse_vps_lines(vps_knowledge_raw, "knowledge")
    parse_vps_lines(vps_gemma_raw, "gemma_extractions")

    # 3. Merge inventories
    all_keys = sorted(list(set(local_books.keys()) | set(vps_books.keys())))
    
    # 4. Generate Markdown
    md = []
    md.append("# Astrological Books Inventory (Local vs VPS Sync Status)")
    md.append("\nThis artifact lists all classical/modern books, PDF scans, and JSON extractions found across the **Local Workspace** and the **Live VPS Server** (`46.28.44.225`).")
    md.append("\n## Summary Table")
    md.append("\n| Book / Extraction File | Category / Type | Local Status | VPS Status | Sync Status |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for key in all_keys:
        loc = local_books.get(key)
        vp = vps_books.get(key)
        
        # Determine file type description
        ext = Path(key).suffix.upper()
        if ext == ".PDF":
            ftype = "Original PDF Scan"
        elif ext == ".JSON":
            ftype = "Gemma JSON Rules"
        elif "_raw" in key:
            ftype = "Raw Text Transcription"
        else:
            ftype = "Extracted Text"
            
        local_desc = "Absent"
        if loc:
            size_kb = round(loc["local_size"] / 1024, 1)
            local_desc = f"Present ({size_kb} KB)"
            
        vps_desc = "Absent"
        if vp:
            size_kb = round(vp["size"] / 1024, 1)
            vps_desc = f"Present ({size_kb} KB)"
            
        # Determine sync status
        if loc and vp:
            if loc["local_size"] == vp["size"]:
                status = "🟢 Synced (Identical)"
            else:
                status = "🟡 Size Mismatch (Out of Sync)"
        elif loc:
            status = "🔴 Local Only"
        else:
            status = "🔵 VPS Only"
            
        md.append(f"| `{key}` | {ftype} | {local_desc} | {vps_desc} | {status} |")
        
    # Write to artifact directory
    artifact_path = Path("C:/Users/chive/.gemini/antigravity/brain/380f2a9a-0f97-479e-bfff-d6c3bcb77703/books_inventory.md")
    artifact_path.write_text("\n".join(md), encoding="utf-8")
    print(f"Inventory successfully written to artifact: {artifact_path}")

if __name__ == "__main__":
    main()
