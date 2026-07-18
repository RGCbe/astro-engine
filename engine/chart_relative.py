"""
Chart-relative event scoring.

Replaces universal karaka tables (e.g. "Jupiter for children, Venus for
marriage") with per-chart factors derived from the actual chart:

    - 10th lord, 10th house occupant      → CAREER events
    - 5th lord, 5th from Jupiter         → CHILDREN_BORN
    - 7th lord, Venus, 2nd-from-Venus    → MARRIAGE / DIVORCE
    - 8th lord, 12th lord, 6th lord      → DEATH / HEALTH_CRISIS / MAJOR_LOSS
    - Atmakaraka (AK), Putrakaraka (PK), Stree-karaka (StK) — Jaimini chara
    - Lagna lord, Hora lord, Ghatika lord

This is what classical scholars actually do — assess the *specific chart's*
significators, not generic karakas. Empirically should produce sharper LRs
because the lord set is narrower per event per chart.

API:
    chart_relative_lords(chart, event_type) → set of relevant lords for THIS chart
    score_event_relative(chart, event_type, md_lord, ad_lord)
        → {tier, matched_factor, evidence}

Per the truth-only directive: when chart-relative scoring disagrees with
the universal karaka set, both views are surfaced via `compare_views`.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

# Sign indices: 0=Aries .. 11=Pisces
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}


@dataclass
class ChartFactors:
    """Per-chart factors used for relative scoring."""
    lagna_lord: str
    h2_lord: str   # wealth, family, speech
    h4_lord: str   # home, mother, vehicle, comforts
    h5_lord: str   # children, intellect, romance
    h6_lord: str   # enemies, disease, debt
    h7_lord: str   # spouse, partnership
    h8_lord: str   # longevity, accidents, secrets
    h9_lord: str   # fortune, dharma, guru
    h10_lord: str  # career, status, public role
    h11_lord: str  # gains, elder siblings, fulfillment
    h12_lord: str  # loss, foreign, moksha
    AK: str        # Atmakaraka (highest-degree planet, Jaimini)
    AmK: str       # Amatyakaraka (2nd-highest)
    BhK: str       # Bhratrukaraka (3rd) — siblings
    MK: str        # Matrukaraka (4th) — mother
    PK: str        # Putrakaraka (5th) — children
    GK: str        # Gnatikaraka (6th) — disease/cousins
    DK: str        # Darakaraka (7th-from-end, lowest) — spouse


def _planet_house_lords(chart) -> dict[int, str]:
    """Get lord of each house 1-12 in this chart."""
    lagna_sign = int(chart.lagna_lon // 30)
    out = {}
    for h in range(1, 13):
        sign = (lagna_sign + h - 1) % 12
        out[h] = SIGN_LORD[sign]
    return out


def _jaimini_karakas(chart) -> dict[str, str]:
    """Compute Jaimini chara karakas (8 grahas excluding Ketu).

    Sort 7 planets (Sun..Saturn) + Rahu by *advancing degree in their sign*
    (highest degree = AK). Rahu's degree is reversed (30 - actual deg).
    """
    candidates = []
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        deg_in_sign = lon - int(lon // 30) * 30
        if p == "Rahu":
            deg_in_sign = 30 - deg_in_sign
        candidates.append((deg_in_sign, p))
    candidates.sort(reverse=True)   # highest deg first
    karaka_names = ["AK", "AmK", "BhK", "MK", "PK", "GK", "DK"]
    out = {}
    # Standard Jaimini: 7 grahas → 7 karakas; Rahu sometimes excluded (then DK becomes 8th-lowest)
    # We use the 8-graha system (PVR Narasimha Rao convention).
    for k, (_, planet) in zip(karaka_names, candidates[:7]):
        out[k] = planet
    # DK = lowest (last in sorted desc)
    if len(candidates) >= 8:
        out["DK"] = candidates[-1][1]
    elif len(candidates) >= 1:
        out["DK"] = candidates[-1][1]
    return out


def chart_factors(chart) -> ChartFactors:
    """Build the per-chart factors needed for relative event scoring."""
    house_lords = _planet_house_lords(chart)
    karakas = _jaimini_karakas(chart)
    return ChartFactors(
        lagna_lord=house_lords[1],
        h2_lord=house_lords[2], h4_lord=house_lords[4],
        h5_lord=house_lords[5], h6_lord=house_lords[6],
        h7_lord=house_lords[7], h8_lord=house_lords[8],
        h9_lord=house_lords[9], h10_lord=house_lords[10],
        h11_lord=house_lords[11], h12_lord=house_lords[12],
        AK=karakas.get("AK", ""), AmK=karakas.get("AmK", ""),
        BhK=karakas.get("BhK", ""), MK=karakas.get("MK", ""),
        PK=karakas.get("PK", ""), GK=karakas.get("GK", ""),
        DK=karakas.get("DK", ""),
    )


# ─── Per-event chart-relative lord sets ────────────────────────────────────
def chart_relative_lords(chart, event_type: str) -> dict[str, list[str]]:
    """Return chart-specific lord sets for `event_type`, ordered by tier:
        primary  : the most direct chart-relative significators
        secondary: supporting/dispositor factors
    """
    f = chart_factors(chart)
    out = {"primary": [], "secondary": []}

    if event_type == "MARRIAGE":
        # Primary: 7th lord, Darakaraka (Jaimini spouse-karaka), Venus
        out["primary"] = [f.h7_lord, f.DK, "Venus"]
        # Secondary: 2nd lord (family-extension), Jupiter (for women), 11th lord
        out["secondary"] = [f.h2_lord, "Jupiter", f.h11_lord]

    elif event_type == "CHILDREN_BORN":
        # Primary: 5th lord, Putrakaraka, Jupiter
        out["primary"] = [f.h5_lord, f.PK, "Jupiter"]
        # Secondary: 9th from 5th (=lagna), 7th lord (parenthood through marriage)
        out["secondary"] = [f.lagna_lord, f.h7_lord, "Saturn"]

    elif event_type == "CAREER_PEAK" or event_type == "CAREER_START":
        # Primary: 10th lord, Atmakaraka, Amatyakaraka
        out["primary"] = [f.h10_lord, f.AK, f.AmK]
        # Secondary: lagna lord, 6th lord (service), 11th lord (gains from career)
        out["secondary"] = [f.lagna_lord, f.h6_lord, f.h11_lord]

    elif event_type == "POLITICAL_OFFICE":
        # Primary: 10th lord, AmK, AK
        out["primary"] = [f.h10_lord, f.AmK, f.AK]
        # Secondary: 11th lord, 6th lord (defeating opponents)
        out["secondary"] = [f.h11_lord, f.h6_lord, "Sun"]

    elif event_type == "FOUND_BUSINESS":
        # Primary: AmK (career-actualizer), 10th lord, 11th lord (new gains)
        out["primary"] = [f.AmK, f.h10_lord, f.h11_lord]
        # Secondary: lagna lord (initiative), Mercury (commerce)
        out["secondary"] = [f.lagna_lord, "Mercury", f.h7_lord]

    elif event_type == "AWARD":
        # Primary: 5th lord (recognition), 11th lord (fulfilled desires), AK
        out["primary"] = [f.h5_lord, f.h11_lord, f.AK]
        # Secondary: 9th lord (fortune), Jupiter
        out["secondary"] = [f.h9_lord, "Jupiter", "Sun"]

    elif event_type == "DEATH":
        # Primary: 8th lord (longevity), 2nd lord (maraka), 7th lord (maraka)
        out["primary"] = [f.h8_lord, f.h2_lord, f.h7_lord]
        # Secondary: 12th lord, 6th lord
        out["secondary"] = [f.h12_lord, f.h6_lord, "Saturn"]

    elif event_type == "HEALTH_CRISIS":
        # Primary: 6th lord (disease), 8th lord, GK (disease karaka)
        out["primary"] = [f.h6_lord, f.h8_lord, f.GK]
        # Secondary: lagna lord, Saturn (chronic), Mars (acute/surgery)
        out["secondary"] = [f.lagna_lord, "Saturn", "Mars"]

    elif event_type == "DIVORCE":
        # Primary: 7th lord, DK, Mars (Mangal dosha)
        out["primary"] = [f.h7_lord, f.DK, "Mars"]
        # Secondary: Saturn (separation), Rahu, 6th lord (disputes)
        out["secondary"] = ["Saturn", "Rahu", f.h6_lord]

    elif event_type == "MAJOR_LOSS":
        # Primary: 12th lord (loss), 8th lord (sudden), 6th lord
        out["primary"] = [f.h12_lord, f.h8_lord, f.h6_lord]
        # Secondary: 2nd lord (wealth-loss), Saturn, Rahu
        out["secondary"] = [f.h2_lord, "Saturn", "Rahu"]

    elif event_type == "IMPRISONMENT":
        # Primary: 12th lord (confinement), 8th lord, Saturn
        out["primary"] = [f.h12_lord, f.h8_lord, "Saturn"]
        # Secondary: 6th lord (legal trouble), Rahu, Mars
        out["secondary"] = [f.h6_lord, "Rahu", "Mars"]

    elif event_type == "EXILE":
        # Primary: 12th lord (foreign/loss), 9th lord (long journey), Rahu
        out["primary"] = [f.h12_lord, f.h9_lord, "Rahu"]
        # Secondary: 4th lord (uprooted from home), Saturn
        out["secondary"] = [f.h4_lord, "Saturn", "Ketu"]

    elif event_type == "SPIRITUAL_AWAKENING":
        # Primary: 12th lord (moksha), 9th lord (dharma), Ketu
        out["primary"] = [f.h12_lord, f.h9_lord, "Ketu"]
        # Secondary: Jupiter, 5th lord (purva-punya), Saturn (renunciation)
        out["secondary"] = ["Jupiter", f.h5_lord, "Saturn"]

    elif event_type == "SCANDAL":
        # Primary: 6th lord, 8th lord, Rahu
        out["primary"] = [f.h6_lord, f.h8_lord, "Rahu"]
        # Secondary: 12th lord, Mars
        out["secondary"] = [f.h12_lord, "Mars", "Mercury"]

    # Deduplicate while preserving order
    out["primary"] = list(OrderedDict.fromkeys(out["primary"]))
    out["secondary"] = list(OrderedDict.fromkeys(
        x for x in out["secondary"] if x not in out["primary"]
    ))
    return out


def score_event_relative(chart, event_type: str, md_lord: str | None,
                         ad_lord: str | None) -> dict:
    """Score MD/AD lords against chart-relative significator set."""
    sets = chart_relative_lords(chart, event_type)
    primary = set(sets["primary"])
    secondary = set(sets["secondary"])

    def classify(lord):
        if lord is None:
            return "miss"
        if lord in primary:
            return "primary"
        if lord in secondary:
            return "secondary"
        return "miss"

    md_t = classify(md_lord)
    ad_t = classify(ad_lord)
    rank = {"primary": 2, "secondary": 1, "miss": 0}
    best_tier = md_t if rank[md_t] >= rank[ad_t] else ad_t

    matched_factors = []
    for lord in (md_lord, ad_lord):
        if lord in primary:
            # Find what role this lord plays in the chart
            f = chart_factors(chart)
            roles = []
            for attr in ("lagna_lord", "h2_lord", "h4_lord", "h5_lord", "h6_lord",
                         "h7_lord", "h8_lord", "h9_lord", "h10_lord", "h11_lord",
                         "h12_lord", "AK", "AmK", "BhK", "MK", "PK", "GK", "DK"):
                if getattr(f, attr) == lord:
                    roles.append(attr)
            matched_factors.append({"lord": lord, "tier": "primary", "roles": roles})
        elif lord in secondary:
            matched_factors.append({"lord": lord, "tier": "secondary", "roles": []})

    return {
        "event_type": event_type,
        "md": md_lord, "ad": ad_lord,
        "md_tier": md_t, "ad_tier": ad_t, "best_tier": best_tier,
        "primary_set":   sorted(primary),
        "secondary_set": sorted(secondary),
        "matched_factors": matched_factors,
    }
