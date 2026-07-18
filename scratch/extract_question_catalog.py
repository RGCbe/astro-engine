"""
Extract all structured Question Records from STRUCTURE BASE volumes 10A-10Q
and save them as a JSON file for loading into the Knowledge Graph.
"""
import re, json, os

MASTER_TXT = r"f:\astro\STRUCTURE BASE\MASTER_STRUCTURE_BASE.txt"
OUT_PATH    = r"f:\astro\gemma_extractions\question_catalog.json"

with open(MASTER_TXT, encoding="utf-8") as f:
    full_text = f.read()

# ── parse every Q#### block ────────────────────────────────────────────────
# Pattern: Q followed by 4 digits, then the question text on next lines,
# then domain, life_stage, placement columns (tab-separated or newline-separated)

question_pattern = re.compile(
    r"(Q\d{4})\r?\n"           # Q ID
    r"([^\r\n]+)\r?\n"          # question text
    r"([^\r\nQ]+?)\r?\n"        # domain (optional)
    r"([^\r\nQ]+?)\r?\n"        # life stage
    r"([^\r\nQ]+?)(?=\r?\n)",   # placement
    re.MULTILINE
)

# Determine volume for each question
volume_text_split = re.split(r"={80}\r?\n(Volume_\S+)\r?\n=", full_text)

questions = []
current_volume = "Unknown"

# Simpler approach: scan line by line
lines = full_text.splitlines()
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Track current volume
    if line.startswith("Volume_10"):
        current_volume = line
        i += 1
        continue
    
    # Match question ID line
    if re.match(r"^Q\d{4}$", line):
        qid = line
        qtext = lines[i+1].strip() if i+1 < len(lines) else ""
        domain = lines[i+2].strip() if i+2 < len(lines) else ""
        life_stage = lines[i+3].strip() if i+3 < len(lines) else ""
        placement = lines[i+4].strip() if i+4 < len(lines) else ""
        
        # Skip if question text looks like a header/junk
        if qtext and len(qtext) > 3 and not qtext.startswith("=") and not qtext.startswith("AstroReport"):
            questions.append({
                "id": qid,
                "question": qtext,
                "domain": domain,
                "life_stage": life_stage,
                "placement": placement,
                "volume": current_volume
            })
        i += 5
        continue
    
    i += 1

# Deduplicate by ID
seen = {}
for q in questions:
    seen[q["id"]] = q
unique_questions = sorted(seen.values(), key=lambda x: x["id"])

# Save
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump({"total": len(unique_questions), "questions": unique_questions}, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(unique_questions)} unique questions")
print(f"Saved to: {OUT_PATH}")
print()
# Print first 20
for q in unique_questions[:20]:
    print(f"  {q['id']}: {q['question']} [{q['domain']} | {q['life_stage']}]")
