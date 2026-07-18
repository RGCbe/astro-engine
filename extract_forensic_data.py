import json
import sys
import os



def main():
    with open('charts/manoj_chart.json', 'r', encoding='utf-8') as f:
        chart = json.load(f)

    pos = chart['positions']
    lagna_idx = chart['lagna_idx']
    
    # Calculate D9, D10, D60 if possible using engine/vargas.py or similar logic. 
    # Wait, vargas.py might just be a dict mapping. Let's just output D1 and D9 from manoj_chart.json if they exist.
    # Actually manoj_chart.json has navamsa_rasi in positions!
    
    # Let's extract Dasha
    # compute_dasha_full usually takes the chart's moon longitude.
    
    md_content = f"""# Forensic Verification Report

**Subject:** {chart['name']}
**Birth Details:** {chart['birth']['day']} May {chart['birth']['year']}, {chart['birth']['hour']}:{chart['birth']['min']} IST
**Location:** {chart['birth']['place_en']} (Lat: {chart['birth']['lat']}, Lon: {chart['birth']['lon']})
**Ayanamsa:** {chart.get('ayanamsa', 'Unknown')}

## 1. D1 Planetary Longitudes (Rasi Chart)

| Planet | Longitude (Total) | Sign | Degree | Nakshatra | Pada |
|--------|-------------------|------|--------|-----------|------|
"""
    for planet, data in pos.items():
        md_content += f"| {planet} | {data.get('lon', 0):.4f}° | {data.get('rasi', '')} | {data.get('deg', 0):.4f}° | {data.get('nak', '')} | {data.get('pada', '')} |\n"

    md_content += f"""
## 2. D9 (Navamsa) Placements

| Planet | D9 Sign |
|--------|---------|
"""
    for planet, data in pos.items():
        md_content += f"| {planet} | {data.get('navamsa_rasi', 'Unknown')} |\n"
        
    md_content += """
## 3. Verification Checklist

Use your independent software (Jagannath Hora, Kala, etc.) to verify these outputs:

- [ ] Does the D1 Ascendant match exactly?
- [ ] Do the planetary degrees match to within 1-2 arcminutes?
- [ ] Do the D9 Navamsa sign placements match?
- [ ] Does the Vimshottari Dasha sequence align? (Check Moon's Nakshatra Pada)
- [ ] Are the Shadbala values within acceptable tolerance?

If any of these fail, our `pyswisseph` integration or timezone logic requires patching.
"""
    
    print(md_content)
        
if __name__ == '__main__':
    main()
