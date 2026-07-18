import sys
sys.stdout.reconfigure(encoding='utf-8')
from main import calculate_jathagam, BirthData

bd = BirthData(year=1955, month=2, day=24, time="19:15", lat=37.775, lon=-122.418, focus="career")
data = calculate_jathagam(bd)

print(f"=== CORPUS READING: Steve Jobs chart ===")
print(f"Lagna: {data['lagnam']} | Moon: {data['janma_rasi']} | Nak: {data['janma_nakshatra']}")
print(f"Maha Dasha: {data['current_dasha']} | Antardasha: {data['current_antardasha']}")
print()

for hr in data['house_predictions']:
    rules = hr.get('corpus_rules', [])
    if rules:
        print(f"--- {hr['planet']} in H{hr['house']} ({hr['rasi']}) ---")
        for i, r in enumerate(rules[:3]):
            print(f"  [{r['source']}]: {r['text'][:200]}")
        print()
