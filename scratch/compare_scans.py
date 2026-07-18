import json
import sys
from pathlib import Path

def main():
    local_path = Path("scratch/local_scan.json")
    vps_path = Path("scratch/vps_scan.json")
    
    if not local_path.exists() or not vps_path.exists():
        print(f"Error: Make sure both {local_path} and {vps_path} exist.")
        sys.exit(1)
        
    local_data = json.loads(local_path.read_text(encoding="utf-8-sig"))
    vps_data = json.loads(vps_path.read_text(encoding="utf-8-sig"))
    
    local_only = []
    vps_only = []
    mismatched = []
    matched = []
    
    # Check local files against VPS
    for rel_path, info in local_data.items():
        if rel_path not in vps_data:
            local_only.append((rel_path, info["size"]))
        else:
            vps_info = vps_data[rel_path]
            if info["md5"] != vps_info["md5"]:
                mismatched.append((rel_path, info["size"], vps_info["size"]))
            else:
                matched.append((rel_path, info["size"]))
                
    # Check VPS files against local
    for rel_path, info in vps_data.items():
        if rel_path not in local_data:
            vps_only.append((rel_path, info["size"]))
            
    out_lines = []
    out_lines.append("# Local vs VPS File Comparison Report")
    out_lines.append(f"**Total files matched exactly (same MD5):** {len(matched)}\n")
    
    out_lines.append("## Files Only Locally")
    if local_only:
        out_lines.append("| File Path | Size (Bytes) |")
        out_lines.append("|---|---|")
        for p, sz in sorted(local_only):
            out_lines.append(f"| {p} | {sz:,} |")
    else:
        out_lines.append("*None*")
    out_lines.append("")
    
    out_lines.append("## Files Only on VPS")
    if vps_only:
        out_lines.append("| File Path | Size (Bytes) |")
        out_lines.append("|---|---|")
        for p, sz in sorted(vps_only):
            out_lines.append(f"| {p} | {sz:,} |")
    else:
        out_lines.append("*None*")
    out_lines.append("")
    
    out_lines.append("## Mismatched Files (Modified)")
    if mismatched:
        out_lines.append("| File Path | Local Size (B) | VPS Size (B) |")
        out_lines.append("|---|---|---|")
        for p, l_sz, v_sz in sorted(mismatched):
            out_lines.append(f"| {p} | {l_sz:,} | {v_sz:,} |")
    else:
        out_lines.append("*None*")
        
    out_text = "\n".join(out_lines)
    Path("scratch/diff_report.md").write_text(out_text, encoding="utf-8")
    print(f"Diff report successfully written to scratch/diff_report.md! Matched: {len(matched)}, Local only: {len(local_only)}, VPS only: {len(vps_only)}, Mismatched: {len(mismatched)}")
        
if __name__ == "__main__":
    main()
