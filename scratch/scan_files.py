import os
import hashlib
import json
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".claude", ".pytest_cache", "_archive", "node_modules", "_research"}
EXCLUDE_FILES = {".env", "scan_files.py"}

def calculate_md5(filepath):
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def scan_directory(base_dir):
    base_path = Path(base_dir).resolve()
    result = {}
    
    for root, dirs, files in os.walk(base_path):
        # Filter directories in-place to prevent walking down excluded ones
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file in EXCLUDE_FILES:
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(base_path).as_posix()
            
            size = file_path.stat().st_size
            md5 = calculate_md5(file_path)
            
            result[rel_path] = {
                "size": size,
                "md5": md5
            }
            
    return result

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    res = scan_directory(target_dir)
    json_str = json.dumps(res, indent=2)
    
    if output_file:
        Path(output_file).write_text(json_str, encoding="utf-8")
        print(f"Scanned {len(res)} files. Saved to {output_file}")
    else:
        print(json_str)

if __name__ == "__main__":
    main()
