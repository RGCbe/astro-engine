import re, json
from collections import Counter
from pathlib import Path
from engine.chart import compute_chart

chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                      lat=11.0168, lon=76.9558, name="Manoj")
house_of = chart.house_of
blob = json.loads(Path("logic_base/ALL_COMBINATIONS.json").read_text(encoding="utf-8"))
combos = blob["combinations"]

BENEFIC = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFIC = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
PLANETS = BENEFIC | MALEFIC
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
       "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12}


def as_houses(v):
    if isinstance(v, list):
        return sorted({int(h) for h in v if str(h).strip().isdigit() and 1 <= int(h) <= 12})
    return sorted({int(h) for h in re.findall(r"\d{1,2}", str(v)) if 1 <= int(h) <= 12})


def houses_in(t):
    hs = set()
    for m in re.finditer(r"(\d{1,2})(?:st|nd|rd|th)", t or ""):
        if 1 <= int(m.group(1)) <= 12:
            hs.add(int(m.group(1)))
    for w, n in ORD.items():
        if re.search(r"\b" + w + r"\b", t or "", re.I):
            hs.add(n)
    return hs


def pol_cls(pol):
    pol = (pol or "").lower()
    return BENEFIC if "benefic" in pol else (MALEFIC if "malefic" in pol else PLANETS)


# --- multi_house: firing rate under several thresholds ---
mh = combos["multi_house"]
def occ_count(hs, cls):
    return len({h for p, h in house_of.items() if h in hs and p in cls})
thr = {"any>=1": 0, "occ>=2": 0, "all_houses": 0}
for x in mh:
    hs = as_houses(x.get("houses"))
    cls = pol_cls(x.get("polarity"))
    oc = occ_count(hs, cls)
    if oc >= 1: thr["any>=1"] += 1
    if oc >= 2: thr["occ>=2"] += 1
    if hs and oc == len(hs): thr["all_houses"] += 1
print("=== multi_house (33) firing on Manoj ===", thr)

# --- conditional: STRICT parser ---
cond = combos["conditional"]
NEG_COMPLEX = re.compile(
    r"other than|unless|\bnot\b|\bno\b|in strength|conjunction|conjoin|aspect|"
    r"lord of the rasi|dispositor|exchange|parivart|associate|debilit|exalt|"
    r"combust|retrograd", re.I)


def parse_pred(t):
    if not t or NEG_COMPLEX.search(t):
        return None
    hs = houses_in(t)
    if not hs:
        return None
    tl = t.lower()
    if "benefic" in tl:
        return ("class", "benefic", frozenset(hs))
    if "malefic" in tl:
        return ("class", "malefic", frozenset(hs))
    named = tuple(p for p in PLANETS if re.search(r"\b" + p + r"\b", t))
    if named:
        return ("planets", named, frozenset(hs))
    return None


def holds(pred):
    kind, who, hs = pred
    occ = [p for p, h in house_of.items() if h in hs]
    if kind == "class":
        cls = BENEFIC if who == "benefic" else MALEFIC
        return any(p in cls for p in occ)
    return any(p in occ for p in who)


parseable = fire = 0
examples = []
for x in cond:
    p1 = parse_pred(x.get("condition_1"))
    p2 = parse_pred(x.get("condition_2"))
    if p1 and p2:
        parseable += 1
        if holds(p1) and holds(p2):
            fire += 1
            if len(examples) < 6:
                examples.append((x.get("book"), p1, p2,
                                 str(x.get("effect", ""))[:60]))
print(f"=== conditional (1206) STRICT: both-parse={parseable}  would-fire={fire} ===")
for b, p1, p2, eff in examples:
    print(f"  [{b}] {p1} AND {p2} | {eff!r}")
