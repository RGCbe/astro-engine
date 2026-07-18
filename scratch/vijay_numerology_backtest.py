"""
Forensic Numerology Backtest over Thalapathy Vijay's 68-Film Filmography.
Calculates the Chaldæan Name Number for every movie and correlates it
with the commercial box office outcome (Hits/Blockbusters vs. Flops)
relative to his 4-4 (Rahu) birth numerology grid.
"""
import sys
import re

# Phonetic Chaldæan values mapping
CHALDEAN_VALUES = {
    'A': 1, 'I': 1, 'J': 1, 'Y': 1, 'Q': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

PLANET_LARDS = {
    1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu",
    5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"
}

def digit_root(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def calculate_name_number(name: str) -> int:
    sanitized = re.sub(r'[^A-Z]', '', name.upper())
    total = sum(CHALDEAN_VALUES[c] for c in sanitized if c in CHALDEAN_VALUES)
    return digit_root(total)

def run_numerology_backtest():
    # Full 68-film timeline of Thalapathy Vijay as lead actor
    films = [
        {"num": 1, "name": "Naalaiya Theerpu", "date": "1992-12-04", "status": "Flop"},
        {"num": 2, "name": "Sendhoorapandi", "date": "1993-12-24", "status": "Hit"},
        {"num": 3, "name": "Rasigan", "date": "1994-07-08", "status": "Hit"},
        {"num": 4, "name": "Deva", "date": "1995-02-14", "status": "Hit"},
        {"num": 5, "name": "Rajavin Parvaiyile", "date": "1995-08-04", "status": "Flop"},
        {"num": 6, "name": "Vishnu", "date": "1995-08-18", "status": "Flop"},
        {"num": 7, "name": "Chandralekha", "date": "1995-10-23", "status": "Flop"},
        {"num": 8, "name": "Coimbatore Mapillai", "date": "1996-01-15", "status": "Hit"},
        {"num": 9, "name": "Poove Unakkaga", "date": "1996-02-15", "status": "Blockbuster"},
        {"num": 10, "name": "Vasantha Vasal", "date": "1996-03-15", "status": "Flop"},
        {"num": 11, "name": "Maanbumigu Maanavan", "date": "1996-04-12", "status": "Flop"},
        {"num": 12, "name": "Selva", "date": "1996-12-05", "status": "Flop"},
        {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop"},
        {"num": 14, "name": "Love Today", "date": "1997-05-09", "status": "Blockbuster"},
        {"num": 15, "name": "Once More", "date": "1997-07-04", "status": "Hit"},
        {"num": 16, "name": "Nerrukku Ner", "date": "1997-09-06", "status": "Hit"},
        {"num": 17, "name": "Kadhalukku Mariyadhai", "date": "1997-12-19", "status": "Blockbuster"},
        {"num": 18, "name": "Ninaithen Vandhai", "date": "1998-04-10", "status": "Hit"},
        {"num": 19, "name": "Priyamudan", "date": "1998-06-12", "status": "Hit"},
        {"num": 20, "name": "Nilaave Vaa", "date": "1998-08-14", "status": "Flop"},
        {"num": 21, "name": "Thulladha Manamum Thullum", "date": "1999-01-29", "status": "Blockbuster"},
        {"num": 22, "name": "Endrendrum Kadhal", "date": "1999-03-05", "status": "Flop"},
        {"num": 23, "name": "Nenjinile", "date": "1999-06-25", "status": "Flop"},
        {"num": 24, "name": "Minsara Kanna", "date": "1999-09-09", "status": "Flop"},
        {"num": 25, "name": "Kannukkul Nilavu", "date": "2000-01-14", "status": "Flop"},
        {"num": 26, "name": "Kushi", "date": "2000-05-19", "status": "Blockbuster"},
        {"num": 27, "name": "Priyamaanavale", "date": "2000-10-26", "status": "Blockbuster"},
        {"num": 28, "name": "Friends", "date": "2001-01-14", "status": "Blockbuster"},
        {"num": 29, "name": "Badri", "date": "2001-04-12", "status": "Hit"},
        {"num": 30, "name": "Shahjahan", "date": "2001-11-14", "status": "Flop"},
        {"num": 31, "name": "Thamizhan", "date": "2002-04-12", "status": "Flop"},
        {"num": 32, "name": "Youth", "date": "2002-07-19", "status": "Hit"},
        {"num": 33, "name": "Bagavathi", "date": "2002-11-04", "status": "Hit"},
        {"num": 34, "name": "Vaseegara", "date": "2003-01-15", "status": "Flop"},
        {"num": 35, "name": "Pudhiya Geethai", "date": "2003-05-08", "status": "Flop"},
        {"num": 36, "name": "Thirumalai", "date": "2003-10-24", "status": "Blockbuster"},
        {"num": 37, "name": "Udhaya", "date": "2004-03-26", "status": "Flop"},
        {"num": 38, "name": "Ghilli", "date": "2004-04-17", "status": "Blockbuster"},
        {"num": 39, "name": "Madurey", "date": "2004-08-29", "status": "Hit"},
        {"num": 40, "name": "Thirupaachi", "date": "2005-01-14", "status": "Blockbuster"},
        {"num": 41, "name": "Sachien", "date": "2005-04-14", "status": "Hit"},
        {"num": 42, "name": "Sivakasi", "date": "2005-11-01", "status": "Blockbuster"},
        {"num": 43, "name": "Aathi", "date": "2006-01-15", "status": "Flop"},
        {"num": 44, "name": "Pokkiri", "date": "2007-01-12", "status": "Blockbuster"},
        {"num": 45, "name": "Azhagiya Tamil Magan", "date": "2007-11-08", "status": "Flop"},
        {"num": 46, "name": "Kuruvi", "date": "2008-05-03", "status": "Flop"},
        {"num": 47, "name": "Pandhayam", "date": "2008-09-19", "status": "Flop"},
        {"num": 48, "name": "Villu", "date": "2009-01-12", "status": "Flop"},
        {"num": 49, "name": "Vettaikaaran", "date": "2009-12-18", "status": "Hit"},
        {"num": 50, "name": "Sura", "date": "2010-04-30", "status": "Flop"},
        {"num": 51, "name": "Kaavalan", "date": "2011-01-15", "status": "Hit"},
        {"num": 52, "name": "Velayudham", "date": "2011-10-26", "status": "Blockbuster"},
        {"num": 53, "name": "Nanban", "date": "2012-01-12", "status": "Blockbuster"},
        {"num": 54, "name": "Thuppakki", "date": "2012-11-13", "status": "Blockbuster"},
        {"num": 55, "name": "Thalaivaa", "date": "2013-08-09", "status": "Flop"},
        {"num": 56, "name": "Jilla", "date": "2014-01-10", "status": "Hit"},
        {"num": 57, "name": "Kaththi", "date": "2014-10-22", "status": "Blockbuster"},
        {"num": 58, "name": "Puli", "date": "2015-10-01", "status": "Flop"},
        {"num": 59, "name": "Theri", "date": "2016-04-14", "status": "Blockbuster"},
        {"num": 60, "name": "Bairavaa", "date": "2017-01-12", "status": "Hit"},
        {"num": 61, "name": "Mersal", "date": "2017-10-18", "status": "Blockbuster"},
        {"num": 62, "name": "Sarkar", "date": "2018-11-06", "status": "Blockbuster"},
        {"num": 63, "name": "Bigil", "date": "2019-10-25", "status": "Blockbuster"},
        {"num": 64, "name": "Master", "date": "2021-01-13", "status": "Blockbuster"},
        {"num": 65, "name": "Beast", "date": "2022-04-13", "status": "Hit"},
        {"num": 66, "name": "Varisu", "date": "2023-01-11", "status": "Blockbuster"},
        {"num": 67, "name": "Leo", "date": "2023-10-19", "status": "Blockbuster"},
        {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster"}
    ]

    print("=" * 80)
    print("      THALAPATHY VIJAY 68-FILM FILMOGRAPHY FORENSIC NUMEROLOGY AUDIT")
    print("=" * 80)
    
    # Track statistics per name number (1 to 9)
    num_stats = {i: {"hits": 0, "flops": 0} for i in range(1, 10)}
    
    print(f"{'No.':<4} | {'Movie Name':<28} | {'Outcome':<12} | {'Name Num':<9} | {'Vibrational Lord':<16}")
    print("-" * 80)
    
    for f in films:
        num = calculate_name_number(f["name"])
        lord = PLANET_LARDS[num]
        
        is_hit = f["status"] in ["Hit", "Blockbuster"]
        if is_hit:
            num_stats[num]["hits"] += 1
        else:
            num_stats[num]["flops"] += 1
            
        print(f"{f['num']:<4} | {f['name']:<28} | {f['status']:<12} | {num:<9} | {lord:<16}")
        
    print("\n" + "=" * 80)
    print("      AGGREGATE NUMEROLOGICAL OUTCOMES SUMMARY")
    print("=" * 80)
    print(f"{'Num':<4} | {'Lord':<12} | {'Hits':<5} | {'Flops':<6} | {'Total':<6} | {'Hit Ratio':<10} | {'Vibrational Quality for Vijay (4-4 Grid)':<30}")
    print("-" * 80)
    
    # Compatibility mapping for Vijay (Vidhi=4, Bhagya=4)
    # Friends of 4: 2, 6, 8
    # Hostile to 4: 1, 5, 9
    # Neutral to 4: 3, 7
    compatibility = {
        1: ("Hostile", "Sun opposes Rahu"),
        2: ("Friendly", "Moon is a dynamic helper to Rahu"),
        3: ("Neutral", "Jupiter is a spiritual neutral"),
        4: ("Conjoined", "Double-Rahu amplifier"),
        5: ("Hostile", "Mercury represents business blocks to Rahu"),
        6: ("Friendly", "Venus (Guru of Daityas) supports Rahu"),
        7: ("Neutral", "Ketu represents axial shadow"),
        8: ("Friendly", "Saturn (Mitra of Rahu) gives massive structural focus"),
        9: ("Hostile", "Mars (Angaraka) causes high friction/accidents")
    }
    
    for i in range(1, 10):
        stats = num_stats[i]
        hits = stats["hits"]
        flops = stats["flops"]
        total = hits + flops
        ratio_str = f"{(hits / total * 100):.1f}%" if total > 0 else "0.0%"
        lord = PLANET_LARDS[i]
        quality, note = compatibility[i]
        
        print(f"{i:<4} | {lord:<12} | {hits:<5} | {flops:<6} | {total:<6} | {ratio_str:<10} | {quality:<10} ({note})")
    
    # Calculate overall stats for friendly vs hostile names
    friendly_hits = sum(num_stats[n]["hits"] for n in [2, 6, 8])
    friendly_flops = sum(num_stats[n]["flops"] for n in [2, 6, 8])
    friendly_total = friendly_hits + friendly_flops
    friendly_ratio = (friendly_hits / friendly_total * 100) if friendly_total > 0 else 0
    
    hostile_hits = sum(num_stats[n]["hits"] for n in [1, 5, 9])
    hostile_flops = sum(num_stats[n]["flops"] for n in [1, 5, 9])
    hostile_total = hostile_hits + hostile_flops
    hostile_ratio = (hostile_hits / hostile_total * 100) if hostile_total > 0 else 0
    
    print("\n" + "=" * 80)
    print("      SCIENTIFIC COMPATIBILITY GRID VERIFICATION")
    print("=" * 80)
    print(f" Friendly Movie Names (2, 6, 8) : {friendly_hits} Hits / {friendly_total} Films ({friendly_ratio:.2f}% Success Rate)")
    print(f" Hostile Movie Names (1, 5, 9)  : {hostile_hits} Hits / {hostile_total} Films ({hostile_ratio:.2f}% Success Rate)")
    print(f" Conjoined Rahu Names (4)       : {num_stats[4]['hits']} Hits / {num_stats[4]['hits'] + num_stats[4]['flops']} Films")
    print("=" * 80)

if __name__ == "__main__":
    run_numerology_backtest()
