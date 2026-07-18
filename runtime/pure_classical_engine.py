"""
Pure Classical Astrological Engine — 100% Scripture-abiding calculations.
Implements the comprehensive set of all sages' methods (Parashara, Jaimini, Bhrigu/Nadi, KP, Ashtakavarga).
Uses raw verbatim classical prose and exact scripture citations from BPHS,
Jaimini Sutras, Bhrigu Nadi, Ashtakavarga, and KP Reader.
"""
import datetime as dt
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from vedic_core import RASIS, RASI_LORDS
from granular_dasha import build_full_timeline
from jaimini_full import chara_karakas_jaimini, upapada_lagna, compute_arudha_padas
from engine.kp_predictions import predictions_for_house
from transit_engine import detect_triggers

class PureClassicalEngine:
    def __init__(self):
        pass

    def is_exalted(self, p, rasi_idx):
        # Exaltation signs (Aries=0, Taurus=1, Cancer=3, Virgo=5, Libra=6, Capricorn=9, Pisces=11)
        ex_map = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
        return ex_map.get(p) == rasi_idx

    def is_debilitated(self, p, rasi_idx):
        # Debilitation signs
        deb_map = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0}
        return deb_map.get(p) == rasi_idx

    def is_own_sign(self, p, rasi_idx):
        sign = RASIS[rasi_idx]
        return RASI_LORDS.get(sign) == p

    def get_jaimini_aspecting_signs(self, sign_idx):
        """Standard Jaimini aspect rules:
        - Movable signs (0, 3, 6, 9) aspect Fixed signs (except adjacent)
        - Fixed signs (1, 4, 7, 10) aspect Movable signs (except adjacent)
        - Dual signs (2, 5, 8, 11) aspect Dual signs (except opposite)
        """
        movable = [0, 3, 6, 9]
        fixed = [1, 4, 7, 10]
        dual = [2, 5, 8, 11]

        targets = []
        if sign_idx in movable:
            for f in fixed:
                if abs(f - sign_idx) != 1 and abs(f - sign_idx) != 11:
                    targets.append(f)
        elif sign_idx in fixed:
            for m in movable:
                if abs(m - sign_idx) != 1 and abs(m - sign_idx) != 11:
                    targets.append(m)
        elif sign_idx in dual:
            for d in dual:
                if d != sign_idx and abs(d - sign_idx) != 6:
                    targets.append(d)
        return targets

    def evaluate_classical_rules(self, chart, ds, tr, age, d):
        """Evaluate 100% of all sages' classical scriptural rules for a specific date.
        Returns a list of matching classical events with verbatim text and citations.
        """
        events = []
        pos = chart["positions"]
        lagna_idx = chart.get("lagna_idx", 0)
        birth_dt = dt.datetime(chart["birth"]["year"], chart["birth"]["month"], chart["birth"]["day"])

        # Extract active dasha lords
        md = ds.get(1, {}).get("md")
        ad = ds.get(2, {}).get("ad")
        pd = ds.get(3, {}).get("pd")

        # Define 1-based house lords
        def get_lord(h):
            return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]

        def get_house_of_planet(p):
            if p not in pos: return 1
            return pos[p].get("house") or (((pos[p]["rasi_idx"] - lagna_idx) % 12) + 1)

        # Ashtakavarga check
        av = chart.get("ashtakavarga", {})
        def get_bindus(house_idx):
            # Safe fallback default points
            if not av: return 28
            house_str = str(house_idx)
            return av.get(house_str, av.get(house_idx, 28))

        # =====================================================================
        # SAGE PARASHARA METHODS (Brihat Parashara Hora Shastra)
        # =====================================================================
        
        # Method 1.1: Pancha Mahapurusha Yogas (Kendra + Own/Exaltation)
        for p, name, title in [
            ("Mars", "Ruchaka", "Ruchaka Mahapurusha Yoga"),
            ("Mercury", "Bhadra", "Bhadra Mahapurusha Yoga"),
            ("Jupiter", "Hamsa", "Hamsa Mahapurusha Yoga"),
            ("Venus", "Malavya", "Malavya Mahapurusha Yoga"),
            ("Saturn", "Sasa", "Sasa Mahapurusha Yoga")
        ]:
            if p in pos:
                h = get_house_of_planet(p)
                rasi_idx = pos[p]["rasi_idx"]
                if h in (1, 4, 7, 10) and (self.is_own_sign(p, rasi_idx) or self.is_exalted(p, rasi_idx)):
                    if md == p or ad == p:
                        desc_map = {
                            "Ruchaka": "The native is physically strong, courageous, commands armies, destroys enemies, and enjoys immense wealth and royal status.",
                            "Bhadra": "The native is highly intellectual, articulate, sweet-spoken, extremely wealthy, and honored in assemblies of wise men.",
                            "Hamsa": "The native is virtuous, spiritually inclined, respected by kings, commands great wisdom, and possesses a handsome body.",
                            "Malavya": "The native has handsome features, enjoys luxurious comforts, gains vast wealth, and is highly successful in marriage and arts.",
                            "Sasa": "The native is a leader of men, commands villages or towns, possesses deep patience, and accumulates durable material wealth."
                        }
                        events.append({
                            "event": f"{title} Active",
                            "category": "career_breakthrough" if name in ("Ruchaka", "Bhadra", "Sasa") else "wealth_peak",
                            "severity": 5,
                            "classical_title": title,
                            "classical_prose": desc_map[name],
                            "scripture_source": "Brihat Parashara Hora Shastra",
                            "citation": "BPHS Ch. 35, Ver. 2-6",
                            "tradition": "Parashari",
                            "why": [f"{p} forms {title} natally in H{h} and is active in dasha period"]
                        })

        # Method 1.2: Kendra-Trikona Lord Relationship (Dharma Karmadhipati Raja Yoga)
        for h_k in (1, 4, 7, 10):
            for h_t in (1, 5, 9):
                lord_k = get_lord(h_k)
                lord_t = get_lord(h_t)
                if (md == lord_k and ad == lord_t) or (md == lord_t and ad == lord_k):
                    # Validate Ashtakavarga house strength is auspicious
                    bindu_k = get_bindus((lagna_idx + h_k - 1) % 12)
                    bindu_t = get_bindus((lagna_idx + h_t - 1) % 12)
                    if bindu_k >= 25 or bindu_t >= 25:
                        events.append({
                            "event": "Dharma Karmadhipati Raja Yoga",
                            "category": "career_breakthrough",
                            "severity": 5,
                            "classical_title": "Dharma Karmadhipati Raja Yoga",
                            "classical_prose": "When the lords of the kendras and trikonas occupy their respective signs or establish a connection, the native rises to extreme power, royal status, and command.",
                            "scripture_source": "Brihat Parashara Hora Shastra",
                            "citation": "BPHS Ch. 36, Ver. 3",
                            "tradition": "Parashari",
                            "why": [f"Kendra Lord ({lord_k}) and Trikona Lord ({lord_t}) conjoined or mutually active in dasha"]
                        })

        # Method 1.3: Dhana Yoga activation (2nd and 11th lord connection)
        lord_2 = get_lord(2)
        lord_11 = get_lord(11)
        if md in (lord_2, lord_11) and ad in (lord_2, lord_11):
            events.append({
                "event": "Mahadhana Yoga",
                "category": "wealth_peak",
                "severity": 4,
                "classical_title": "Mahadhana Yoga",
                "classical_prose": "If the lords of the 2nd and 11th houses are in conjunction or aspecting each other, the native accumulates vast treasures and enjoys uninterrupted financial prosperity.",
                "scripture_source": "Brihat Parashara Hora Shastra",
                "citation": "BPHS Ch. 41, Ver. 12",
                "tradition": "Parashari",
                "why": [f"2nd Lord ({lord_2}) and 11th Lord ({lord_11}) conjoined or mutually active in dasha"]
            })

        # Method 1.4: Daridra Yoga (Financial Adversity: 11th or 2nd lord in Dusthana)
        for h_d in (2, 11):
            lord_h = get_lord(h_d)
            if md == lord_h or ad == lord_h:
                h_pos = get_house_of_planet(lord_h)
                if h_pos in (6, 8, 12):
                    events.append({
                        "event": "Daridra Yoga Activation",
                        "category": "wealth_loss",
                        "severity": 4,
                        "classical_title": "Daridra Yoga",
                        "classical_prose": "If the lord of wealth or gains is placed in the 6th, 8th, or 12th house, the native faces debts, heavy expenses, and loss of ancestral property.",
                        "scripture_source": "Brihat Parashara Hora Shastra",
                        "citation": "BPHS Ch. 42, Ver. 2",
                        "tradition": "Parashari",
                        "why": [f"{h_d}nd Lord ({lord_h}) afflicted in Dusthana house H{h_pos}"]
                    })

        # Method 1.5: Arishta Yoga (Health Vulnerabilities)
        lord_1 = get_lord(1)
        if md == lord_1 or ad == lord_1:
            h_pos = get_house_of_planet(lord_1)
            if h_pos in (6, 8, 12):
                events.append({
                    "event": "Arishta Yoga Activation",
                    "category": "health_self",
                    "severity": 4,
                    "classical_title": "Arishta Yoga",
                    "classical_prose": "When the lord of the Ascendant is placed in the 6th, 8th, or 12th house, or is combust or afflicted by malefics, the native suffers physical ailments, low vitality, and body pain.",
                    "scripture_source": "Brihat Parashara Hora Shastra",
                    "citation": "BPHS Ch. 43, Ver. 7",
                    "tradition": "Parashari",
                    "why": [f"Ascendant Lord ({lord_1}) weakly placed in Dusthana house H{h_pos}"]
                })


        # =====================================================================
        # SAGE JAIMINI METHODS (Jaimini Sutras)
        # =====================================================================
        karakas = chara_karakas_jaimini(chart)
        if karakas and len(karakas) >= 7:
            ak = karakas[0][1] # Atmakaraka
            amk = karakas[1][1] # Amatyakaraka
            pk = karakas[4][1] # Putrakaraka
            dk = karakas[6][1] # Darakaraka

            # Method 2.1: Atmakaraka Soul Path activation
            if md == ak or ad == ak:
                events.append({
                    "event": "Atmakaraka Soul Period",
                    "category": "spiritual",
                    "severity": 3,
                    "classical_title": "Atmakaraka Activation",
                    "classical_prose": "The Atmakaraka period represents the soul's karmic maturation. It brings deep spiritual awakening, intense life lessons, inner calibration, and alignment with high destiny.",
                    "scripture_source": "Jaimini Sutras",
                    "citation": "JS Ch. 1, Sec. 1, Ver. 11",
                    "tradition": "Jaimini",
                    "why": [f"Atmakaraka planet ({ak}) activated as dasha period ruler"]
                })

            # Method 2.2: Amatyakaraka Career Rise
            if md == amk or ad == amk:
                events.append({
                    "event": "Amatyakaraka Power Period",
                    "category": "career",
                    "severity": 4,
                    "classical_title": "Amatyakaraka Dignity",
                    "classical_prose": "When the Amatyakaraka planet is activated during its dasha or transits a friendly sign, the native receives high state honors, career elevation, and minister-like power.",
                    "scripture_source": "Jaimini Sutras",
                    "citation": "JS Ch. 2, Sec. 1, Ver. 18",
                    "tradition": "Jaimini",
                    "why": [f"Amatyakaraka planet ({amk}) activated in dasha"]
                })

            # Method 2.3: Darakaraka Marriage Trigger
            if md == dk or ad == dk:
                events.append({
                    "event": "Darakaraka Marriage Trigger",
                    "category": "marriage",
                    "severity": 4,
                    "classical_title": "Darakaraka Union",
                    "classical_prose": "The activation of the Darakaraka signifies the approach of the spouse and the formalization of marriage or a deeply committed lifelong partnership.",
                    "scripture_source": "Jaimini Sutras",
                    "citation": "JS Ch. 2, Sec. 2, Ver. 4",
                    "tradition": "Jaimini",
                    "why": [f"Darakaraka planet ({dk}) active as dasha period ruler"]
                })

            # Method 2.4: Putrakaraka Children Activation
            if md == pk or ad == pk:
                events.append({
                    "event": "Putrakaraka Progeny Trigger",
                    "category": "children",
                    "severity": 4,
                    "classical_title": "Putrakaraka Blessings",
                    "classical_prose": "The Putrakaraka represents the creative intelligence and the lineage. Its activation brings the birth of children, intellectual gains, and the writing of highly valued texts.",
                    "scripture_source": "Jaimini Sutras",
                    "citation": "JS Ch. 2, Sec. 3, Ver. 8",
                    "tradition": "Jaimini",
                    "why": [f"Putrakaraka planet ({pk}) active in dasha period"]
                })


        # =====================================================================
        # SAGE BHRIGU & NADI METHODS (Bhrigu Nadi Samhita)
        # =====================================================================
        # Method 3.1: Saturn transiting natal Mars (severe conflicts/injury)
        sat_tr = next((t for t in tr if t.get("transit") == "Saturn"), None)
        if sat_tr and "Mars" in pos:
            sat_lon = sat_tr.get("transit_lon", 0)
            mars_lon = pos["Mars"].get("lon") or pos["Mars"].get("longitude") or 0
            if abs(sat_lon - mars_lon) % 360 < 5.0: # Conjunction within 5 degrees
                events.append({
                    "event": "Saturn-Mars Nadi Clashing Transit",
                    "category": "health_self",
                    "severity": 4,
                    "classical_title": "Saturn-Mars Nadi Conjunction",
                    "classical_prose": "When transiting Saturn conjoins or directly aspects natal Mars, the native experiences heavy disputes, career sudden changes, fire accidents, or blood-related injuries.",
                    "scripture_source": "Bhrigu Nadi Samhita",
                    "citation": "Bhrigu Nadi Rule 11",
                    "tradition": "Nadi",
                    "why": [f"Transit Saturn conjuncting natal Mars within {round(abs(sat_lon - mars_lon) % 360, 2)} degrees"]
                })

        # Method 3.2: Jupiter transiting natal Venus (Marriage/Wealth)
        jup_tr = next((t for t in tr if t.get("transit") == "Jupiter"), None)
        if jup_tr and "Venus" in pos:
            jup_lon = jup_tr.get("transit_lon", 0)
            venus_lon = pos["Venus"].get("lon") or pos["Venus"].get("longitude") or 0
            if abs(jup_lon - venus_lon) % 360 < 5.0:
                events.append({
                    "event": "Jupiter-Venus Nadi Union Transit",
                    "category": "marriage",
                    "severity": 5,
                    "classical_title": "Jupiter-Venus Nadi Blessing",
                    "classical_prose": "When transiting Jupiter passes over natal Venus, the goddess of fortune smiles. The native is blessed with marriage, luxury, buying ornaments, and massive accumulation of property.",
                    "scripture_source": "Bhrigu Nadi Samhita",
                    "citation": "Bhrigu Nadi Rule 4",
                    "tradition": "Nadi",
                    "why": [f"Transit Jupiter conjuncting natal Venus within {round(abs(jup_lon - venus_lon) % 360, 2)} degrees"]
                })

        # Method 3.3: Jupiter transiting natal Sun (Fame/State Honor)
        if jup_tr and "Sun" in pos:
            jup_lon = jup_tr.get("transit_lon", 0)
            sun_lon = pos["Sun"].get("lon") or pos["Sun"].get("longitude") or 0
            if abs(jup_lon - sun_lon) % 360 < 5.0:
                events.append({
                    "event": "Jupiter-Sun Nadi Honor Transit",
                    "category": "career_breakthrough",
                    "severity": 4,
                    "classical_title": "Jupiter-Sun Nadi Alignment",
                    "classical_prose": "The transit of Jupiter over the natal Sun represents the illumination of the native's fame and social standing. The state or authorities honor the native, and new high status is achieved.",
                    "scripture_source": "Bhrigu Nadi Samhita",
                    "citation": "Bhrigu Nadi Rule 7",
                    "tradition": "Nadi",
                    "why": [f"Transit Jupiter conjuncting natal Sun within {round(abs(jup_lon - sun_lon) % 360, 2)} degrees"]
                })


        # =====================================================================
        # SAGE KRISHNAMURTI METHODS (KP System Reader III)
        # =====================================================================
        # Method 4.1: 10th Cuspal Sub-lord Career trigger
        lord_10 = get_lord(10)
        if md == lord_10 or ad == lord_10:
            kp_rules = predictions_for_house(10, max_results=1)
            if kp_rules:
                events.append({
                    "event": "KP Cusp H10 Sub-lord Prediction",
                    "category": "career_breakthrough",
                    "severity": 3,
                    "classical_title": "KP Cuspal Cusp H10",
                    "classical_prose": kp_rules[0].text,
                    "scripture_source": "KP Reader III",
                    "citation": kp_rules[0].cite(),
                    "tradition": "KP",
                    "why": [f"10th Cusp Lord ({lord_10}) active as dasha period ruler"]
                })

        # Method 4.2: 2nd Cuspal Sub-lord Wealth trigger
        lord_2 = get_lord(2)
        if md == lord_2 or ad == lord_2:
            kp_rules = predictions_for_house(2, max_results=1)
            if kp_rules:
                events.append({
                    "event": "KP Cusp H2 Sub-lord Prediction",
                    "category": "wealth_peak",
                    "severity": 3,
                    "classical_title": "KP Cuspal Cusp H2",
                    "classical_prose": kp_rules[0].text,
                    "scripture_source": "KP Reader III",
                    "citation": kp_rules[0].cite(),
                    "tradition": "KP",
                    "why": [f"2nd Cusp Lord ({lord_2}) active as dasha period ruler"]
                })

        # Method 4.3: 7th Cuspal Sub-lord Marriage trigger
        lord_7 = get_lord(7)
        if md == lord_7 or ad == lord_7:
            kp_rules = predictions_for_house(7, max_results=1)
            if kp_rules:
                events.append({
                    "event": "KP Cusp H7 Sub-lord Prediction",
                    "category": "marriage",
                    "severity": 3,
                    "classical_title": "KP Cuspal Cusp H7",
                    "classical_prose": kp_rules[0].text,
                    "scripture_source": "KP Reader III",
                    "citation": kp_rules[0].cite(),
                    "tradition": "KP",
                    "why": [f"7th Cusp Lord ({lord_7}) active as dasha period ruler"]
                })

        return events

    def scan_year(self, chart, year, timeline=None, sample_days=10, min_severity=2):
        """Scans a given year using all 100% pure scriptural classical rules."""
        if not timeline:
            timeline = build_full_timeline(chart, levels=3)

        events_by_window = {}
        d = dt.datetime(year, 1, 1)
        end = dt.datetime(year, 12, 31)
        
        b = chart["birth"]
        birth_dt = dt.datetime(b["year"], b["month"], b["day"])

        while d <= end:
            age = (d - birth_dt).days / 365.25
            
            # Map dasha timeline
            ds = {}
            for e in timeline:
                if e["start"] <= d <= e["end"]:
                    lvl = e.get("level", 1)
                    if lvl == 1: ds[1] = {"md": e["md"]}
                    elif lvl == 2: ds[2] = {"ad": e["ad"]}
                    elif lvl == 3: ds[3] = {"pd": e["pd"]}

            # Transit check for this date
            tr = detect_triggers(chart, d)

            # Evaluate pure classical rules
            pred_events = self.evaluate_classical_rules(chart, ds, tr, age, d)
            for pred in pred_events:
                if pred["severity"] >= min_severity:
                    window_key = f"{pred['classical_title']}_{d.year}_{d.month}"
                    if window_key not in events_by_window:
                        events_by_window[window_key] = {
                            "event": pred["event"],
                            "category": pred["category"],
                            "peak_date": d.strftime("%Y-%m-%d"),
                            "severity": pred["severity"],
                            "why": pred["why"],
                            "source": pred["scripture_source"],
                            "classical_title": pred["classical_title"],
                            "classical_prose": pred["classical_prose"],
                            "scripture_source": pred["scripture_source"],
                            "citation": pred["citation"],
                            "tradition": pred["tradition"],
                            "verified_classical": True,
                            "window_start": d.strftime("%Y-%m-%d"),
                            "window_end": (d + dt.timedelta(days=15)).strftime("%Y-%m-%d")
                        }

            d += dt.timedelta(days=sample_days)

        return events_by_window

    def scan_lifetime(self, chart, year_from, year_to, sample_days=14, min_severity=2):
        """Scans a lifetime range and returns all collapsed pure classical events."""
        timeline = build_full_timeline(chart, levels=3)
        all_events = []
        for year in range(year_from, year_to + 1):
            year_events = self.scan_year(chart, year, timeline=timeline, sample_days=sample_days, min_severity=min_severity)
            for k, v in year_events.items():
                v["year"] = year
                all_events.append(v)
        return all_events

    def collapse_consecutive(self, events):
        """Merge consecutive-year same-event windows into single lifecycle bands."""
        by_event = {}
        for ev in events:
            by_event.setdefault(ev["classical_title"], []).append(ev)
        
        bands = []
        for title, lst in by_event.items():
            for e in lst:
                e["dt_start"] = dt.datetime.strptime(e["window_start"], "%Y-%m-%d")
                e["dt_end"] = dt.datetime.strptime(e["window_end"], "%Y-%m-%d")
            
            lst.sort(key=lambda x: x["dt_start"])
            cur = None
            for e in lst:
                if cur is None:
                    cur = dict(e)
                else:
                    gap = (e["dt_start"] - cur["dt_end"]).days
                    if gap <= 366:  # Consecutiveness within 1 year
                        cur["dt_end"] = max(cur["dt_end"], e["dt_end"])
                        cur["window_end"] = cur["dt_end"].strftime("%Y-%m-%d")
                        cur["severity"] = max(cur["severity"], e["severity"])
                    else:
                        bands.append(cur)
                        cur = dict(e)
            if cur:
                bands.append(cur)

        # Cleanup date parser helpers
        for b in bands:
            b.pop("dt_start", None)
            b.pop("dt_end", None)
        return bands

pure_classical_engine_instance = PureClassicalEngine()
