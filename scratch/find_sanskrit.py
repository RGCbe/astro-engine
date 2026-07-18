import re

with open(r"f:\Atro\Books\Laghu_Parashari_extracted.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

devanagari_pattern = re.compile(r'[\u0900-\u097f]')

blocks = []
current_block = []

for idx, line in enumerate(lines):
    if devanagari_pattern.search(line):
        current_block.append((idx + 1, line.strip()))
    else:
        if current_block:
            blocks.append(current_block)
            current_block = []
if current_block:
    blocks.append(current_block)

print(f"Found {len(blocks)} Sanskrit blocks:")
for i, block in enumerate(blocks[:30]):
    print(f"\nBlock {i+1} (Line {block[0][0]} to {block[-1][0]}):")
    for line_num, text in block:
        print(f"  {line_num}: {text}")
