"""
sree.pdf-style life chapters — one self-contained chapter per Maha Dasha.

Each chapter contains:
    - Chapter number, planet, year range, age range, theme tagline
    - 3-column header summary (e.g. STRENGTH/RISK/LIFE-THEME)
    - One paragraph narrative intro
    - EXPECT bullets (positive/likely events)
    - WATCH bullets (risks)
    - Detail sub-section: antardasha-by-antardasha specific predictions

This becomes the main spine of the report. All life domains (career,
marriage, money, health) fold INTO each chapter rather than living in
separate sections.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from engine.narrative import _ord, HOUSE_DOMAINS, PLANET_DOMAINS


CHAPTER_THEME = {
    "Sun":     "Authority Phase",
    "Moon":    "Public Visibility Peak",
    "Mars":    "Action / Friction / Transformation",
    "Mercury": "Intellect & Communication Phase",
    "Jupiter": "Wisdom / Settled Phase",
    "Venus":   "Building / Pleasure / Partnership Phase",
    "Saturn":  "Discipline & Long-Build",
    "Rahu":    "Unconventional / Foreign Phase",
    "Ketu":    "Detachment / Inward Turn",
}


def _theme_for_age(planet: str, age_a: int, age_b: int) -> str:
    """Override the planet-default theme when age-band suggests a different
    life-stage (e.g. Mercury MD at age 97 is NOT 'Foundation Years')."""
    base = CHAPTER_THEME.get(planet, "")
    mid = (age_a + age_b) // 2
    if mid < 7:
        return f"{base} (Infancy)"
    if mid < 14:
        return f"{base} (Childhood / School)"
    if mid < 22:
        return f"{base} (Adolescence / Education)"
    if mid < 35:
        return f"{base} (Early Career / Marriage)"
    if mid < 50:
        return f"{base} (Mid-Life Build)"
    if mid < 65:
        return f"{base} (Public Peak / Consolidation)"
    if mid < 80:
        return f"{base} (Elder / Legacy)"
    return f"{base} (Late-Life / Closure)"


def _lord_roles(chart, planet: str) -> str:
    """Return a description of which houses this planet rules in the chart,
    e.g. 'Lagna lord' / '5th & 8th lord' / 'not a house-lord (node)'."""
    SIGN_LORD_MAP = {
        "Mars":    [0, 7], "Venus": [1, 6], "Mercury": [2, 5],
        "Moon":    [3], "Sun": [4], "Jupiter": [8, 11], "Saturn": [9, 10],
        "Rahu":    [], "Ketu": [],
    }
    if planet in ("Rahu", "Ketu"):
        return f"a node (not a house-lord)"
    lagna = int(chart.lagna_lon // 30)
    signs_owned = SIGN_LORD_MAP.get(planet, [])
    houses = sorted(((s - lagna) % 12) + 1 for s in signs_owned)
    if not houses:
        return f"{planet}"
    if len(houses) == 1:
        return f"the {_ord(houses[0])} lord"
    return f"the {_ord(houses[0])} & {_ord(houses[1])} lord"

CHAPTER_SUBHEAD_3COL = {
    "Sun":     ("STATUS", "FATHER ROLE", "AUTHORITY"),
    "Moon":    ("STRENGTH", "HOUSE", "RISK"),
    "Mars":    ("ENERGY", "HEALTH", "RISK"),
    "Mercury": ("STRENGTH", "RISK", "LIFE THEME"),
    "Jupiter": ("LENGTH", "STATUS", "HEALTH"),
    "Venus":   ("CAREER", "MARRIAGE", "WEALTH"),
    "Saturn":  ("MARKER", "MIND", "BODY"),
    "Rahu":    ("LENGTH", "THEME", "INFLUENCE"),
    "Ketu":    ("ENERGY", "THEME", "DIRECTION"),
}

CHAPTER_INTRO_TEMPLATE = {
    "Sun":     "The Sun is the natural karaka of authority and self-expression. In your chart Sun sits in {sign} in your {house} ({domain}) — and is {l_role}. This Maha Dasha activates {domain}-themes through Sun's lens of authority, father, and visibility.",
    "Moon":    "The Moon sits in {sign} in your {house} ({domain}) — and is {l_role}. The Moon's Maha Dasha activates emotional life, mother-bond, and {domain}-themes through the lens of mind and feeling.",
    "Mars":    "Mars sits in {sign} in your {house} ({domain}) — and is {l_role}. Mars's Maha Dasha amplifies courage, friction, technical/surgical capacity, and {domain}-themes through the lens of force.",
    "Mercury": "Mercury sits in {sign} in your {house} ({domain}) — and is {l_role}. Mercury's Maha Dasha activates intellect, speech, analysis, and {domain}-themes through the lens of communication.",
    "Jupiter": "Jupiter sits in {sign} in your {house} ({domain}) — and is {l_role}. Jupiter's Maha Dasha brings expansion, learning, dharma, optimism, and {domain}-themes through the lens of grace.",
    "Venus":   "Venus sits in {sign} in your {house} ({domain}) — and is {l_role}. Venus's Maha Dasha activates pleasure, art, partnership, and {domain}-themes through the lens of beauty and comfort.",
    "Saturn":  "Saturn sits in {sign} in your {house} ({domain}) — and is {l_role}. Saturn's Maha Dasha is structure, work, limit, slow burn — earning {domain}-themes through discipline.",
    "Rahu":    "Rahu sits in {sign} in your {house} ({domain}) — a node, not a house-lord. The Rahu Maha Dasha activates {domain}-themes through the lens of the unconventional, foreign, and ambitious.",
    "Ketu":    "Ketu sits in {sign} in your {house} ({domain}) — a node, not a house-lord. The Ketu Maha Dasha activates {domain}-themes through the lens of detachment, ending, and inward-turn.",
}

CHAPTER_EXPECT_BULLETS = {
    "Sun":     ["Authority offered or asserted in workplace",
                "Career role upgrade or change",
                "Father's health/role recalibration",
                "Tech / foreign opportunity windows",
                "Major dharmic decision in Sun-Jupiter sub",
                "Property and authority growth in Sun-Saturn sub",
                "Career signature work via writing/teaching",
                "Wealth uplift and family expansion at end of MD"],
    "Moon":    ["Career reaches public peak — head of organisation possibly",
                "Public recognition or awards",
                "Caring / public-welfare role manifests fully",
                "Travel + public-facing life",
                "Wealth accumulation steady",
                "Communication-driven success peaks mid-period",
                "Mother's role most active",
                "Final wealth uplift before next MD"],
    "Mars":    ["Research, investigation, occult/depth interest peaks",
                "Possible major surgery or technical breakthrough",
                "Property / inheritance themes activate",
                "Wealth via inheritance or hidden sources",
                "Career: technical/research/depth work peaks",
                "Independent action favoured",
                "Sibling alliances or rivalries surface"],
    "Mercury": ["Healthy infancy if Moon strong",
                "Sharp intellect from early age",
                "Strong academic period age 7-12",
                "Language ability, possible writing aptitude",
                "Mother bond central and supportive",
                "Communication and analysis develop"],
    "Jupiter": ["Family elder role, philanthropy",
                "Stable wealth, traditional respect",
                "Health stable due to Jupiter blessings",
                "Inheritance / will matters become important",
                "Spiritual teaching role",
                "Long life confirmed by Sasa Yoga (if active)"],
    "Venus":   ["Higher education completion (early sub-periods)",
                "Career launch in arts/teaching/finance/communication",
                "First serious relationship → marriage window",
                "Property or vehicle purchase",
                "Foreign / unconventional pivot mid-period",
                "Major dharmic project mid-late period",
                "End-of-MD wealth stability"],
    "Saturn":  ["Centenarian potential if Sasa Yoga active",
                "Settled, wise, respected elder phase",
                "Mental sharpness preserved",
                "Quiet long evening of life",
                "Service to elders / institution-building",
                "Authority via age and persistence"],
    "Rahu":    ["Major spiritual / philosophical phase",
                "Possible foreign teaching, lectures, books",
                "Late-life recognition and influence",
                "Pilgrimage and dharmic travels",
                "Grandchildren period",
                "Wisdom + recognition peak mid-period",
                "Communication legacy work"],
    "Ketu":    ["Early spiritual questioning",
                "Sudden disinterest in earlier paths",
                "Course choice may shift mid-stream",
                "Travel for studies likely",
                "First independence steps",
                "First serious romantic interest end of period"],
}

CHAPTER_WATCH_BULLETS = {
    "Sun":     ["Workplace dispute possible in Sun-Mars sub",
                "Mid-life recalibration intensifies",
                "Sun-Rahu sub: scandal risk if reckless",
                "Health: blood pressure, heart, eyes",
                "Father's health concern through period",
                "Possible income volatility before stabilising",
                "Brief detachment phase in Sun-Ketu sub"],
    "Moon":    ["Mother's last years possibly in this period",
                "Sade Sati 2 may begin late period",
                "Chronic health conditions may surface late period",
                "Emotional intensity high",
                "Workload may overwhelm at peak career",
                "Public criticism risk (high visibility)",
                "Family time pressure"],
    "Mars":    ["Possible major surgery in this period",
                "Father's passing likely (if not earlier)",
                "Conflict with siblings possible",
                "Health watches: blood pressure, accidents",
                "Anger / reactive moments increase"],
    "Mercury": ["Mercury R may cause early speech/learning quirks (resolves)",
                "Sade Sati Phase 1 may overlap (age 2-5 or 3-6)",
                "Early-life pressure on parents",
                "Reserved or thoughtful personality",
                "Possible health issue around age 5-8",
                "Pre-teen introspection borderline isolating"],
    "Jupiter": ["Possible spouse passing in this period",
                "Slowing physical capacity",
                "Family dispute over wealth possible",
                "Inheritance / will responsibilities heavy"],
    "Venus":   ["Sade Sati may overlap mid-period",
                "Mid-period career conflict possible (Venus-Mars sub)",
                "Foreign relocation may strain family",
                "Mother's health watch through Sade Sati",
                "Sade Sati peak may be career-challenging"],
    "Saturn":  ["Health declines slowly",
                "Mobility reduces gradually",
                "Family caregiving pressure increases",
                "Loneliness possible if spouse passed earlier",
                "Death window most likely after MD-end"],
    "Rahu":    ["Rahu can create confusion late in life",
                "Possible health issues from overwork",
                "Family/student boundary issues",
                "Foreign travel may be tiring",
                "Closing transformations late period"],
    "Ketu":    ["Sibling distance or sibling life events",
                "Detachment from material achievements possible",
                "Adolescent identity confusion",
                "Mula nakshatra (if natal) brings disruption with growth"],
}


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


@dataclass
class Chapter:
    n: int
    planet: str
    year_start: int
    year_end: int
    age_start: int
    age_end: int
    theme: str
    subheads: tuple              # 3-tuple of column titles
    subhead_values: tuple        # 3-tuple of values
    intro: str
    expect: list[str]
    watch: list[str]
    antardasha_detail: list[str]
    is_current: bool = False


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    return ((int(lon // 30) - int(chart.lagna_lon // 30)) % 12) + 1


def _planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    return SIGNS[int(lon // 30)]


def _antardasha_bullets(chart, md) -> list[str]:
    """Generate antardasha-level concrete predictions for one mahadasha."""
    out = []
    AD_THEMES = {
        ("Sun", "Sun"):     "Identity recalibration, possible role change. Father's health may need attention.",
        ("Sun", "Moon"):    "Public role activates, emotional visibility rises.",
        ("Sun", "Mars"):    "Conflict period. Workplace dispute or family argument possible. Health watch — blood pressure, heart, eyes.",
        ("Sun", "Rahu"):    "Unconventional opportunity. Technology or foreign exposure peaks. Possible scandal risk if reckless.",
        ("Sun", "Jupiter"): "WISDOM PEAK. Major dharmic decision. Possible spiritual teacher entry. Children's major life event.",
        ("Sun", "Saturn"):  "Slow steady period. Property matters. Authority responsibility increases.",
        ("Sun", "Mercury"): "Communication-driven success. Writing/teaching/consulting peaks. Sibling reconnection.",
        ("Sun", "Ketu"):    "Brief detachment. Spiritual deepening. Possible health pause.",
        ("Sun", "Venus"):   "Wealth uplift, family expansion, end-of-MD recognition.",
        ("Moon", "Moon"):   "Pure Moon energy: career peaks, public visibility maximum, mother bond most active.",
        ("Moon", "Mars"):   "Property purchase or property dispute. Surgical/medical event possible.",
        ("Moon", "Rahu"):   "Foreign / unconventional career pivot. Public scandal risk.",
        ("Moon", "Jupiter"): "Children's major life event. Wisdom peak. Dharmic recognition.",
        ("Moon", "Saturn"): "Sade Sati overlap likely. Career discipline tested. Slow but solid gains.",
        ("Moon", "Mercury"): "Communication-driven success. Books/articles/lectures.",
        ("Moon", "Ketu"):   "Brief withdrawal. Spiritual deepening. Health check.",
        ("Moon", "Venus"):  "Family expansion. Wealth uplift. Aesthetic / artistic recognition.",
        ("Moon", "Sun"):    "Public authority recognised. Father's role important.",
        ("Mars", "Mars"):   "Pure Mars energy: action, courage, possible accident or surgery.",
        ("Mars", "Rahu"):   "Sudden, unconventional events. Foreign opportunity or hazard.",
        ("Mars", "Jupiter"): "Wisdom-tempered action. Constructive courage. Child's major event.",
        ("Mars", "Saturn"): "Hard work pays off slowly. Property / structural work.",
        ("Mars", "Mercury"): "Sharp communication. Technical / scientific writing.",
        ("Mars", "Ketu"):   "Sudden detachment from a project or relationship.",
        ("Mars", "Venus"):  "Romance / partnership intensity. Possible quarrel-then-make-up.",
        ("Mars", "Sun"):    "Authority + force. Recognition through bold action.",
        ("Mars", "Moon"):   "Emotional + physical risk. Mother's health watch.",
        ("Venus", "Venus"): "Pure Venus energy: education, arts, beauty, first love. Possibly post-graduate degree.",
        ("Venus", "Sun"):   "Career identity formation, recognition begins. Father's role important.",
        ("Venus", "Moon"):  "Emotional career fit. Caring/healing role. Marriage possibility opens.",
        ("Venus", "Mars"):  "MARRIAGE LIKELY. Property or vehicle. Sade Sati may begin.",
        ("Venus", "Rahu"):  "Sade Sati peak. Career challenges + rewards. Foreign opportunity or unconventional career move.",
        ("Venus", "Jupiter"): "Sade Sati exit. Major dharmic project. Children if married.",
        ("Venus", "Saturn"): "Hard work pays off. Property accumulation.",
        ("Venus", "Mercury"): "Communication / writing / teaching success. Foreign trade.",
        ("Venus", "Ketu"):  "Brief detachment from the relationship axis.",
        ("Mercury", "Mercury"): "Pure Mercury: speech, study, intellect formation.",
        ("Mercury", "Ketu"): "Adolescent reset. Course / interest change.",
        ("Mercury", "Venus"): "First serious romance possible. Higher studies.",
        ("Mercury", "Sun"):  "Identity through study. Father involvement in education.",
        ("Mercury", "Moon"): "Mother-supported study peak. Caring profession seeds.",
        ("Mercury", "Mars"): "Sharp / argumentative phase. Technical study.",
        ("Mercury", "Rahu"): "Foreign / unconventional study. Tech-heavy path.",
        ("Mercury", "Jupiter"): "Wisdom + intellect united. Teaching potential.",
        ("Mercury", "Saturn"): "Disciplined study. Slow but deep mastery.",
        ("Jupiter", "Jupiter"): "Pure Jupiter energy: wisdom, dharmic peak, grace.",
        ("Jupiter", "Saturn"): "Settled wealth, slow but solid grace.",
        ("Jupiter", "Mercury"): "Books / writing legacy / teaching peak.",
        ("Jupiter", "Ketu"): "Spiritual withdrawal phase.",
        ("Jupiter", "Venus"): "Family elder grace. Wealth + comfort united.",
        ("Jupiter", "Sun"):  "Recognition for wisdom. Public elder role.",
        ("Jupiter", "Moon"): "Family / public service recognition.",
        ("Jupiter", "Mars"): "Constructive force. Wealth-defending action.",
        ("Jupiter", "Rahu"): "Foreign teaching / spiritual confusion possible.",
        ("Saturn", "Saturn"): "Pure Saturn: solitude, discipline, settled mastery.",
        ("Saturn", "Mercury"): "Communication legacy work in old age.",
        ("Saturn", "Ketu"): "Spiritual deepening, withdrawal.",
        ("Saturn", "Venus"): "Late-life comfort and family gathering.",
        ("Saturn", "Sun"):  "Final authority / patriarch recognition.",
        ("Saturn", "Moon"): "Family caregiving role late life.",
        ("Saturn", "Mars"): "Health watch — surgery / accident risk.",
        ("Saturn", "Rahu"): "Final unconventional / foreign chapter possible.",
        ("Saturn", "Jupiter"): "Settled wisdom and grace.",
        ("Rahu", "Rahu"):   "Pure Rahu: foreign / unconventional peak.",
        ("Rahu", "Jupiter"): "Spiritual wisdom + foreign blend. Teacher role.",
        ("Rahu", "Saturn"): "Slow Rahu rewards. Foreign discipline.",
        ("Rahu", "Mercury"): "Tech / communication peak. Foreign business.",
        ("Rahu", "Ketu"): "Eclipse axis activation. Major rebirth event.",
        ("Rahu", "Venus"): "Foreign love / unconventional partnership.",
        ("Rahu", "Sun"):   "Foreign authority. Public Rahu role.",
        ("Rahu", "Moon"):  "Mother-themed foreign event possible.",
        ("Rahu", "Mars"):  "Unconventional force. Possible foreign accident.",
        ("Ketu", "Ketu"):  "Pure Ketu: withdrawal, rebirth, spiritual reset.",
        ("Ketu", "Venus"): "Brief romantic awakening, then detachment.",
        ("Ketu", "Sun"):   "Identity dissolution and rebirth.",
        ("Ketu", "Moon"):  "Emotional withdrawal phase.",
        ("Ketu", "Mars"):  "Sudden ending. Possible accident.",
        ("Ketu", "Rahu"):  "Eclipse axis activation. Reorientation event.",
        ("Ketu", "Jupiter"): "Spiritual elder bond. Pilgrimage.",
        ("Ketu", "Saturn"): "Hard spiritual lesson. Old patterns released.",
        ("Ketu", "Mercury"): "Course change. New study direction.",
    }
    # Antardashas are now in the flat timeline
    from engine.dasha import full_timeline
    from engine.report_chart_details import normalize_chart
    c = normalize_chart(chart)
    ads = [r for r in full_timeline(c, levels=2) if r.get("level") == 2 and r.get("md") == md["md"]]
    for ad in ads:
        sd = ad["start"]
        ed = ad["end"]
        date_a = sd.strftime("%b %Y")
        date_b = ed.strftime("%b %Y")
        theme = AD_THEMES.get((md["md"], ad["ad"]), "")
        out.append(f"**{date_a} → {date_b}** · {md['md']}-{ad['ad']} — {theme}")
    return out


def _event_in_period(planet_owners: set, chapter_planet: str,
                      ad_planet: str | None = None) -> bool:
    """Does an event whose karaka set includes `planet_owners` fire in the
    given (MD, AD) window?"""
    if chapter_planet in planet_owners:
        return True
    if ad_planet and ad_planet in planet_owners:
        return True
    return False


def _enrich_chapter_with_events(ch: 'Chapter', chart) -> None:
    """Inject chart-specific time-anchored events into the chapter's
    EXPECT and WATCH bullets — drawn from accident, education, life_domains,
    afflictions modules."""

    md_planet = ch.planet

    # 1. Accident pattern — does any pattern peak in this MD? Vary the
    #    phrasing so it doesn't read identically across chapters.
    try:
        from engine.accident import detect_accident_patterns
        patterns = detect_accident_patterns(chart)
        for p in patterns:
            if md_planet in p.peak_dashas:
                # Make it MD-lord-specific
                if md_planet == p.peak_dashas[0]:
                    # Primary lord = full detail
                    ch.watch.insert(0,
                        f"⚠ HEALTH WINDOW PEAKS HERE: {p.nature} — body part most exposed: "
                        f"**{p.body_part}**. Pattern source: {p.name}.")
                else:
                    # Secondary lord = brief reminder
                    ch.watch.append(
                        f"Health watch (secondary trigger): "
                        f"the **{p.name}** pattern can be activated; "
                        "see Chapter "
                        f"{p.peak_dashas[0]} for the full body-part detail."
                    )
    except Exception:
        pass

    # 2. Afflictions whose involved planets equal this MD
    try:
        from engine.afflictions import detect_all
        afflictions = detect_all(chart)
        for a in afflictions:
            affected = list(getattr(a, "affected", []))
            if md_planet in affected:
                ch.watch.append(
                    f"Active classical pattern in this period: **{a.name}** "
                    f"({a.severity.lower()}). {a.description}"
                )
    except Exception:
        pass

    # 3. Blessings whose involved planet/lord matches MD
    try:
        from engine.blessings import detect_all as detect_b
        for b in detect_b(chart):
            evidence = (getattr(b, "evidence", "") or "").lower()
            if md_planet.lower() in evidence:
                ch.expect.append(
                    f"Active classical blessing: **{b.name}** "
                    f"({b.strength.lower()}). {b.description}"
                )
    except Exception:
        pass

    # 4. If this MD is the Mercury / Jupiter MD, inject the education prediction
    if md_planet in ("Mercury", "Jupiter") and ch.age_start < 25:
        try:
            from engine.education import predict_subjects
            subs = predict_subjects(chart, top_n=2)
            if subs:
                ch.expect.append(
                    f"Likely subject orientation in this study window: "
                    f"**{subs[0].field}** (primary), "
                    f"{subs[1].field if len(subs) > 1 else ''} (secondary)"
                )
        except Exception:
            pass

    # 5. Marriage window — only inject in the SINGLE chapter spanning the
    #    most likely marriage age (computed from Venus house). One mention,
    #    not repeated.
    if md_planet in ("Venus", "Jupiter", "Moon"):
        try:
            from engine.life_domains import predict_marriage, _planet_house
            m = predict_marriage(chart)
            h_ven = _planet_house(chart, "Venus")
            # Estimate likely marriage age window
            MARRIAGE_AGE_BAND = {
                1: (18, 24), 2: (20, 25), 3: (22, 27), 4: (24, 28),
                5: (20, 26), 6: (28, 35), 7: (24, 30), 8: (32, 42),
                9: (24, 32), 10: (26, 32), 11: (24, 30), 12: (30, 42),
            }
            age_lo, age_hi = MARRIAGE_AGE_BAND.get(h_ven, (24, 30))
            # Only inject if this chapter's age band overlaps the marriage window
            if not (ch.age_end < age_lo or ch.age_start > age_hi):
                ch.expect.append(
                    f"**Marriage window most likely lands here** "
                    f"(probable age {age_lo}–{age_hi}). "
                    f"Spouse profile: {m['spouse_profile']}."
                )
        except Exception:
            pass

    # 6. Career detail in MD of 10L or strong career planet
    if md_planet in ("Sun", "Saturn", "Mars", "Mercury"):
        try:
            from engine.life_domains import predict_career
            c = predict_career(chart)
            ch.expect.append(
                f"Career channel active: **{c['industries_primary']}** "
                f"(via 10th sign), "
                f"{c['industries_secondary']} (via 10L placement)."
            )
        except Exception:
            pass

    # 7. For Rahu/Ketu MD — foreign / spiritual
    if md_planet == "Rahu":
        try:
            from engine.life_domains import predict_foreign
            f = predict_foreign(chart)
            ch.expect.append(
                f"Foreign-travel window opens: **{f['likelihood']}** "
                f"likelihood, direction lean **{f['direction']}**."
            )
        except Exception:
            pass


def build_chapters(chart, today: dt.datetime | None = None,
                   max_age: int = 100
                   ) -> list[Chapter]:
    today = today or dt.datetime.now()
    birth = chart.birth_dt
    chapters: list[Chapter] = []
    for n, md in enumerate(getattr(chart, "vimshottari_periods", []), start=1):
        planet = md["md"]
        # Cap at one human lifetime — vimshottari engine emits 2 full cycles
        if (md["start"] - birth).days // 365 >= max_age:
            break
        sign = _planet_sign(chart, planet)
        house = _planet_house(chart, planet)
        domain = HOUSE_DOMAINS.get(house, "")
        ya = max(0, (md["start"] - birth).days // 365)
        yb = (md["end"] - birth).days // 365
        is_current = md["start"] <= today <= md["end"]

        # Compute chart-derived header values
        l_role = _lord_roles(chart, planet)
        bs = getattr(chart, "bala_summary", {}) or {}
        if planet in (bs.get("strongest") or []):
            strength_tag = "Strong"
        elif planet in (bs.get("weakest") or []):
            strength_tag = "Weak — needs support"
        else:
            strength_tag = "Moderate"
        EXALT = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
                 "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
                 "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"}
        DEBIL = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
                 "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
                 "Saturn": "Aries"}
        own = sign in {
            "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"],
            "Rahu": [], "Ketu": [],
        }.get(planet, [])
        if EXALT.get(planet) == sign:
            dignity = "EXALTED"
        elif DEBIL.get(planet) == sign:
            dignity = "Debilitated"
        elif own:
            dignity = "Own sign"
        else:
            dignity = "Neutral"

        SUB_VAL = {
            "Sun":     (strength_tag, f"in {sign} ({dignity})", f"{_ord(house)} ({domain.split(',')[0]})"),
            "Moon":    (strength_tag, f"in {sign} ({dignity})", f"{_ord(house)} ({domain.split(',')[0]})"),
            "Mars":    (strength_tag, f"in {sign} ({dignity})", f"{_ord(house)} ({domain.split(',')[0]})"),
            "Mercury": (strength_tag, f"in {sign} ({dignity})", f"{_ord(house)} ({domain.split(',')[0]})"),
            "Jupiter": (f"{(yb-ya)} yrs", l_role, f"{_ord(house)} ({domain.split(',')[0]})"),
            "Venus":   (f"{(yb-ya)} yrs", l_role, f"{_ord(house)} ({domain.split(',')[0]})"),
            "Saturn":  (f"{(yb-ya)} yrs", strength_tag, f"{_ord(house)} ({domain.split(',')[0]})"),
            "Rahu":    (f"{(yb-ya)} yrs", f"in {sign}", f"{_ord(house)} ({domain.split(',')[0]})"),
            "Ketu":    (f"{(yb-ya)} yrs", f"in {sign}", f"{_ord(house)} ({domain.split(',')[0]})"),
        }

        intro = CHAPTER_INTRO_TEMPLATE.get(planet, "").format(
            sign=sign,
            house=_ord(house),
            domain=domain.split(",")[0],
            l_role=l_role,
        )

        # Age-aware bullet selection
        expect_bullets = list(CHAPTER_EXPECT_BULLETS.get(planet, []))
        watch_bullets = list(CHAPTER_WATCH_BULLETS.get(planet, []))
        mid_age = (ya + yb) // 2

        # Mercury MD in late life — drop schooling content
        if planet == "Mercury" and mid_age > 25:
            expect_bullets = [b for b in expect_bullets
                              if not any(k in b.lower() for k in
                                         ("infancy", "academic", "age 7",
                                          "mother bond", "first"))]
            expect_bullets.append(
                "Late-life intellectual peak: writing, teaching, "
                "mentoring activates."
            )
        # Ketu MD in infancy — drop adolescent content
        if planet == "Ketu" and yb < 5:
            expect_bullets = [
                "Earliest infancy phase — Ketu cleans residual past-life patterns",
                "Mother's care most active for the child here",
            ]
            watch_bullets = [
                "Sensitive infancy — health watch (typical of Ketu MD at any age)",
            ]
        # Venus MD pre-marriage age (<18) — softer marriage talk
        if planet == "Venus" and yb < 18:
            expect_bullets = [b for b in expect_bullets
                              if "marriage" not in b.lower()
                              and "property" not in b.lower()]

        ch = Chapter(
            n=n, planet=planet,
            year_start=md["start"].year, year_end=md["end"].year,
            age_start=ya, age_end=yb,
            theme=_theme_for_age(planet, ya, yb),
            subheads=CHAPTER_SUBHEAD_3COL.get(planet, ("STRENGTH", "RISK", "THEME")),
            subhead_values=SUB_VAL.get(planet, (strength_tag, sign, _ord(house))),
            intro=intro,
            expect=expect_bullets,
            watch=watch_bullets,
            antardasha_detail=_antardasha_bullets(chart, md),
            is_current=is_current,
        )
        _enrich_chapter_with_events(ch, chart)
        chapters.append(ch)
    return chapters


def render_chapters_markdown(chart) -> str:
    chapters = build_chapters(chart)
    out = []
    for ch in chapters:
        # Section header
        title_line = f"## CHAPTER {ch.n} — {ch.planet} Period"
        if ch.is_current:
            title_line += "  *(YOU ARE HERE)*"
        out.append(title_line)
        out.append("")
        out.append(
            f"**{ch.year_start} – {ch.year_end} · Age {ch.age_start} – "
            f"{ch.age_end} · {ch.theme}**"
        )
        out.append("")
        # 3-column header
        out.append(f"| {ch.subheads[0]} | {ch.subheads[1]} | {ch.subheads[2]} |")
        out.append("|---|---|---|")
        out.append(f"| {ch.subhead_values[0]} | {ch.subhead_values[1]} | {ch.subhead_values[2]} |")
        out.append("")
        # Narrative intro
        out.append(ch.intro)
        out.append("")
        # EXPECT / WATCH two-column-style
        out.append("**✦ EXPECT**")
        out.append("")
        for b in ch.expect:
            out.append(f"- {b}")
        out.append("")
        out.append("**⚠ WATCH**")
        out.append("")
        for b in ch.watch:
            out.append(f"- {b}")
        out.append("")
        # Antardasha detail
        if ch.antardasha_detail:
            out.append("**Sub-period detail (Antardashas):**")
            out.append("")
            for line in ch.antardasha_detail:
                out.append(f"- {line}")
            out.append("")
        out.append("---")
        out.append("")
    return "\n".join(out)
