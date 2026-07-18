import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import SIGN_NAMES
from scratch.vijay_pd_centric_fix import FILMS

async def main():
    corpus = get_corpus()
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    
    # Let's inspect the 16 misses in detail to see if specific classical combinations explain them.
    # Misses under 76.47% model:
    # 1. Kaalamellam Kaathiruppen     | Me-Mo-Mo
    # 2. Endrendrum Kadhal            | Me-Ma-Ve
    # 3. Kushi                        | Me-Ra-Sa
    # 4. Priyamaanavale               | Me-Ra-Me
    # 5. Thamizhan                    | Me-Ju-Sa
    # 6. Vaseegara                    | Me-Ju-Ve
    # 7. Pudhiya Geethai              | Me-Ju-Ve
    # 8. Udhaya                       | Me-Sa-Sa
    # 9. Aathi                        | Me-Sa-Ma
    # 10. Vettaikaaran                 | Ke-Ra-Ju
    # 11. Sura                         | Ke-Ra-Me
    # 12. Puli                         | Ve-Ve-Ju
    
    print("=" * 110)
    print("                ASTROLOGICAL ANALYSIS OF BOUNDARY CONFLICTS (THE 16 MISSES)")
    print("=" * 110)

    # Let's look at the time-resolution overlaps:
    print("[1] Same-Period Split Outcomes (The Time-Resolution Proof):")
    print("-" * 110)
    
    # Check Me-Ma-Ve block:
    # Thulladha Manamum Thullum (Blockbuster) vs Endrendrum Kadhal (Flop)
    print("  Block Me-Ma-Ve (Mercury-Mars-Venus):")
    print("    - 1999-01-29 | Thulladha Manamum Thullum | Target: auspicious   | BO: Blockbuster (HIT)")
    print("    - 1999-03-05 | Endrendrum Kadhal         | Target: inauspicious | BO: Flop (MISS)")
    print("    -> INSIGHT: Both released under Me-Ma-Ve. No single natal chart rule can predict both correctly.")
    print("")

    # Check Me-Ra block:
    # Kushi & Priyamaanavale (Blockbusters) vs Kannukkul Nilavu (Flop) & Shahjahan (Flop)
    print("  Block Me-Ra (Mercury-Rahu):")
    print("    - 2000-01-14 | Kannukkul Nilavu          | Target: inauspicious | BO: Flop (HIT)")
    print("    - 2000-05-19 | Kushi                     | Target: auspicious   | BO: Blockbuster (MISS)")
    print("    - 2000-10-26 | Priyamaanavale            | Target: auspicious   | BO: Blockbuster (MISS)")
    print("    - 2001-11-14 | Shahjahan                 | Target: inauspicious | BO: Flop (HIT)")
    print("    -> INSIGHT: Within Me-Ra, Vijay released two blockbusters and two flops. A split outcome.")
    print("")

    # Check Me-Ju-Ve block:
    # Vaseegara & Pudhiya Geethai (Flops) vs Youth & Bagavathi (Hits)
    # Wait, what was the D-B-P of Youth and Bagavathi?
    # Youth: Me-Ju-Sa (Hit)
    # Bagavathi: Me-Ju-Me (Hit)
    # Vaseegara: Me-Ju-Ve (Flop)
    # Pudhiya Geethai: Me-Ju-Ve (Flop)
    print("  Block Me-Ju (Mercury-Jupiter):")
    print("    - 2002-07-19 | Youth                     | Target: auspicious   | BO: Hit (HIT)")
    print("    - 2002-11-04 | Bagavathi                 | Target: auspicious   | BO: Hit (HIT)")
    print("    - 2003-01-15 | Vaseegara                 | Target: inauspicious | BO: Flop (MISS)")
    print("    - 2003-05-08 | Pudhiya Geethai           | Target: inauspicious | BO: Flop (MISS)")
    print("    -> INSIGHT: Mercury-Jupiter is generally auspicious, but the Venus sub-period (Me-Ju-Ve) brought sudden flops.")
    print("")

    # Check Me-Sa block:
    # Ghilli (Blockbuster) vs Udhaya (Flop) vs Aathi (Flop)
    print("  Block Me-Sa (Mercury-Saturn):")
    print("    - 2004-03-26 | Udhaya                    | Target: inauspicious | BO: Flop (MISS)")
    print("    - 2004-04-17 | Ghilli                    | Target: auspicious   | BO: Blockbuster (HIT)")
    print("    - 2006-01-15 | Aathi                     | Target: inauspicious | BO: Flop (MISS)")
    print("    -> INSIGHT: Within Me-Sa, Vijay released one of his biggest career blockbusters (Ghilli) and two flops.")
    print("")

    print("=" * 110)

if __name__ == "__main__":
    asyncio.run(main())
