import json, sys
sys.path.insert(0, '.')
from pathlib import Path
from engine.corpus import EXCLUDED_BOOKS

suspect_books = [
    ('Dhruva_Nadi_Satyacharya_deep', 373, 1),
    ('Jataka_Chandrika_Kalidas_deep', 1821, 1),
    ('Jataka_Tattvam_Kadalangudi_deep', 3648, 3),
    ('Brihat_Jataka_Sastri_deep', 33590, 5),
    ('Stree_Jataka_Varahamihira_deep', 2829, 5),
    ('Bhrigu_Nadi_TMRao_deep', 5617, 6),
    ('Gochar_Phaladeepika_deep', 7708, 7),
    ('Tajik_Adawal_Encyclopedia_deep', 20279, 9),
    ('Roots_of_Nadi_Naik_deep', 9569, 11),
    ('Deva_Keralam_Vol2_deep', 3727, 14),
    ('Matheseos_Firmicus_Vol1_deep', 15278, 18),
    ('Mansagari_Sanskrit_deep', 25454, 24),
    ('Matheseos_Firmicus_Vol2_deep', 34051, 38),
    ('Carmen_Astrologicum_Dorotheus_deep', 34951, 41),
    ('Hora_Sara_deep', 8266, 41),
    ('Saravali_deep', 16873, 61),
    ('Brihat_Jataka_deep', 107240, 62),
    ('Lal_Kitab_Original_deep', 11660, 135),
]

# Also check well-extracted books for comparison
good_books = [
    ('KP_Reader_3_Predictive_deep', 3017, 4246),
    ('Bhrigu_Samhita_deep', 0, 3412),
    ('Sarvartha_Chintamani_deep', 152670, 2987),
    ('Phaladeepika_deep', 40401, 639),
]

print("=" * 90)
print("  EXTRACTION QUALITY AUDIT")
print("=" * 90)

# Check if books have raw text available for re-extraction
print("\n--- SUSPECT BOOKS (very few rules vs large source) ---\n")
for name, pdf_kb, rule_count in suspect_books:
    fp = Path('gemma_extractions') / (name + '.json')
    data = json.loads(fp.read_text(encoding='utf-8'))
    rules = data if isinstance(data, list) else data.get('rules', data.get('extractions', []))
    
    base = name.replace('_deep','').replace('_gemma','')
    
    # Check raw text availability
    has_raw = any(Path('books').glob(base + '*raw*.txt')) or any(Path('knowledge').glob(base + '*raw*.txt'))
    
    # Check raw text size
    raw_size = 0
    for r in list(Path('books').glob(base + '*raw*.txt')) + list(Path('knowledge').glob(base + '*raw*.txt')):
        raw_size = max(raw_size, r.stat().st_size)
    
    # Estimate expected rules: typical well-extracted book gets ~1 rule per 200-500 bytes of raw text
    # or ~1 rule per 2-5 KB of PDF
    expected_from_pdf = pdf_kb // 3 if pdf_kb > 0 else 0
    expected_from_raw = raw_size // 400 if raw_size > 0 else 0
    expected = max(expected_from_pdf, expected_from_raw)
    
    pct = (rule_count / expected * 100) if expected > 0 else 0
    
    status = "LIKELY INCOMPLETE" if pct < 30 and rule_count < 100 else "POSSIBLY INCOMPLETE" if pct < 50 else "OK"
    
    print(f"  {base:<40} Rules: {rule_count:>5}  PDF: {pdf_kb:>6}KB  Raw: {'YES' if has_raw else 'NO ':>3}  Expected: ~{expected:>5}  Completeness: {pct:>5.1f}%  [{status}]")

print("\n--- WELL-EXTRACTED BOOKS (for comparison) ---\n")
for name, pdf_kb, rule_count in good_books:
    base = name.replace('_deep','').replace('_gemma','')
    fp = Path('gemma_extractions') / (name + '.json')
    print(f"  {base:<40} Rules: {rule_count:>5}  PDF: {pdf_kb:>6}KB  [REFERENCE - GOOD EXTRACTION]")
