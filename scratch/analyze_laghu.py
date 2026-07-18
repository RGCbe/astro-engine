import re

with open(r"f:\Atro\Books\Laghu_Parashari_extracted.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

pattern = re.compile(r'sloka\s*(\d+)', re.IGNORECASE)
matches = []
for idx, line in enumerate(lines):
    m = pattern.search(line)
    if m:
        matches.append((idx + 1, m.group(0), line.strip()))

print(f"Found {len(matches)} matches:")
for idx, match_str, line in matches:
    print(f"Line {idx}: {match_str} -> {line[:100]}")
