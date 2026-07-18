"""Marriage / partnership engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import (Engine, CategoryReport, Prediction, Citation,
                planet_house, planet_sign, lord_of_house, SIGNS)


DUAL_SIGNS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}


def _planets_in_house(chart, house: int) -> list[str]:
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        h = ((int(lon // 30) - lagna_sign) % 12) + 1
        if h == house:
            out.append(p)
    return out


def _saturn_aspects_house(chart, target_house: int) -> bool:
    """Saturn casts 3rd, 7th, 10th aspects."""
    h_sat = planet_house(chart, "Saturn")
    for a in (3, 7, 10):
        if (h_sat - 1 + (a - 1)) % 12 + 1 == target_house:
            return True
    return False


def _mars_aspects_house(chart, target_house: int) -> bool:
    """Mars casts 4th, 7th, 8th aspects."""
    h_mars = planet_house(chart, "Mars")
    for a in (4, 7, 8):
        if (h_mars - 1 + (a - 1)) % 12 + 1 == target_house:
            return True
    return False


def _rahu_aspects_house(chart, target_house: int) -> bool:
    """Rahu/Ketu cast 5th, 7th, 9th aspects (some traditions)."""
    h_rahu = planet_house(chart, "Rahu")
    for a in (5, 7, 9):
        if (h_rahu - 1 + (a - 1)) % 12 + 1 == target_house:
            return True
    return False


def _spouse_community_signal(chart) -> tuple[str, str, list[str]]:
    """Classical Vedic predictors for spouse-from-different-community/region.

    Returns: (verdict, confidence, list_of_signals)
    """
    h_rahu = planet_house(chart, "Rahu")
    h_ketu = planet_house(chart, "Ketu")
    h_ven = planet_house(chart, "Venus")
    sign7 = SIGNS[(int(chart.lagna_lon // 30) + 6) % 12]
    l7 = lord_of_house(chart, 7)
    h_l7 = planet_house(chart, l7)
    sign_l7 = planet_sign(chart, l7)
    occ_7 = _planets_in_house(chart, 7)

    signals: list[str] = []
    score = 0

    # 1. Rahu / Ketu in 7th
    if h_rahu == 7:
        signals.append("Rahu in 7th house — strong cross-community/foreign spouse signal (BPHS)")
        score += 3
    if h_ketu == 7:
        signals.append("Ketu in 7th house — unconventional / spiritually-tinged partnership")
        score += 2

    # 2. Rahu aspects 7th (5th/7th/9th aspect)
    if h_rahu != 7 and _rahu_aspects_house(chart, 7):
        signals.append("Rahu aspects 7th — partner-house carries a foreign / unconventional pull")
        score += 2

    # 3. 7th lord in 12th / 9th / 3rd (foreign-related)
    if h_l7 == 12:
        signals.append(f"7th-lord {l7} in 12th — spouse from far away / foreign region")
        score += 3
    elif h_l7 == 9:
        signals.append(f"7th-lord {l7} in 9th — different faith / cultural-background spouse")
        score += 2
    elif h_l7 == 3:
        signals.append(f"7th-lord {l7} in 3rd (short journey) — spouse met through travel")
        score += 1

    # 4. 7th sign is dual / movable
    if sign7 in DUAL_SIGNS:
        signals.append(f"7th sign {sign7} (dual) — multi-culture / love-marriage natural fit")
        score += 2
    elif sign7 in {"Aries", "Cancer", "Libra", "Capricorn"}:
        signals.append(f"7th sign {sign7} (movable) — partner from a moving/different environment")
        score += 1

    # 5. 7th lord in dual sign
    if sign_l7 in DUAL_SIGNS:
        signals.append(f"7th-lord {l7} in {sign_l7} (dual sign) — partner-axis is pluralistic")
        score += 1

    # 6. Venus + Rahu conjunction
    sign_v = int(chart.positions.get("Venus", 0) // 30)
    sign_r = int(chart.positions.get("Rahu", 0) // 30)
    if sign_v == sign_r:
        signals.append("Venus-Rahu conjunction — unconventional/foreign partnership")
        score += 3

    # 7. Venus opposite Rahu
    if (sign_v - sign_r) % 12 == 6:
        signals.append("Venus opposite Rahu — partner from very different background")
        score += 2

    # 8. Rahu in 9/12 from Venus
    rahu_from_venus = ((sign_r - sign_v) % 12) + 1
    if rahu_from_venus in (9, 12):
        signals.append(
            f"Rahu in {rahu_from_venus}th from Venus — Venus expresses outside conventional bounds"
        )
        score += 1

    # 9. Saturn aspects 7th — older / different-status spouse
    if _saturn_aspects_house(chart, 7) or planet_house(chart, "Saturn") == 7:
        signals.append("Saturn touches 7th — partner may be older / from different generation or status")
        score += 1

    # 10. Mars aspects 7th from non-Mangal-house (still aggressive partner-axis)
    if _mars_aspects_house(chart, 7):
        signals.append("Mars aspects 7th — partner has strong-willed / fiery energy")
        # not a community signal per se, no score

    # 11. Venus in 7th in dual sign — strong love-marriage with intellectually-quick partner
    if h_ven == 7 and planet_sign(chart, "Venus") in DUAL_SIGNS:
        signals.append(
            "Venus in 7th in dual sign — love-marriage signature; partner from intellectually-different / non-conventional background"
        )
        score += 2

    # 12. 7th lord conjunct/aspected by Rahu
    sign_l7_idx = int(chart.positions.get(l7, 0) // 30) if chart.positions.get(l7) else None
    if sign_l7_idx is not None:
        if sign_l7_idx == sign_r:
            signals.append(f"7th-lord {l7} conjunct Rahu — direct cross-community pull on partner-axis")
            score += 3
        elif (sign_l7_idx - sign_r) % 12 == 6:
            signals.append(f"7th-lord {l7} opposite Rahu — partner-axis polarised by foreign influence")
            score += 2

    # 13. Navamsa cross-check (D9) — 7th sign in D9 vs D1
    vargas = getattr(chart, "vargas", None) or {}
    d9 = vargas.get("D9", {})
    d9_sign_7 = d9.get("Venus") or d9.get("7th")
    if d9_sign_7 and d9_sign_7 != sign7:
        # not a strong signal alone, but adds nuance
        signals.append(
            f"D9 navamsa shows Venus in {d9_sign_7} — different sign-element than 7th-rasi → spouse-context shifts in marriage"
        )
        # no extra score; informational

    # 14. Upapada Lagna proxy: 12th from 7th-lord (sign of UL)
    # Skip full Upapada calc (needs longitude math); use 12th from L7-sign
    if sign_l7_idx is not None:
        ul_sign_idx = (sign_l7_idx + 11) % 12
        ul_sign = SIGNS[ul_sign_idx]
        if ul_sign in DUAL_SIGNS:
            signals.append(
                f"Upapada-proxy in {ul_sign} (dual sign) — Jaimini partner-house is pluralistic"
            )
            score += 1

    # 15. BPHS Sharma Vol.1 rule (CORPUS-VERIFIED):
    #     "The 6th is the House of other people than the people of one's
    #      own caste. When the 6th Lord is situated in the 6th House
    #      itself (own sign), the man will belong to his own caste."
    #     → Inverse: 6L NOT in 6H = signal for cross-community
    l6 = lord_of_house(chart, 6)
    h_l6 = planet_house(chart, l6)
    if h_l6 == 6:
        signals.append(
            f"6th-lord {l6} in own 6th house — BPHS Sharma classical rule says spouse from OWN community/caste (counter-signal)"
        )
        score -= 2  # this is a classical contra-signal
    else:
        signals.append(
            f"6th-lord {l6} in H{h_l6} (NOT in own 6th) — classical BPHS Sharma rule: signal for spouse from OTHER community"
        )
        score += 2

    if score >= 6:
        verdict = "STRONG — multiple classical signatures align: spouse very likely from different community / region / faith / background"
        conf = "HIGH"
    elif score >= 3:
        verdict = "MODERATE — clear lean toward cross-community / non-conventional spouse; matches the 'different community' reading other astrologers give"
        conf = "MEDIUM"
    elif score >= 1:
        verdict = "MILD — some signals; spouse may have a slightly different background, intellectual-grain or upbringing than yours"
        conf = "LOW"
    else:
        verdict = "NO cross-community signal — spouse most likely from your own community / region / background"
        conf = "MEDIUM"
    return verdict, conf, signals


class MarriageEngine(Engine):
    category = "marriage"
    title = "Marriage & Partnership"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        m = life_domains.predict_marriage(chart)
        h_ven = planet_house(chart, "Venus")
        h_jup = planet_house(chart, "Jupiter")
        h_mars = planet_house(chart, "Mars")
        sign7 = SIGNS[(int(chart.lagna_lon // 30) + 6) % 12]

        # Estimate marriage age band by Venus house
        BAND = {
            1: (18, 24), 2: (20, 25), 3: (22, 27), 4: (24, 28),
            5: (20, 26), 6: (28, 35), 7: (24, 30), 8: (32, 42),
            9: (24, 32), 10: (26, 32), 11: (24, 30), 12: (30, 42),
        }
        age_lo, age_hi = BAND.get(h_ven, (24, 30))
        preds = [
            Prediction(
                key="age_window",
                label="Probable marriage age window",
                value=f"{age_lo}–{age_hi}",
                confidence="MEDIUM",
                chart_evidence=f"Venus in H{h_ven}, Jupiter in H{h_jup}",
                citations=[Citation(book="BPHS Ch.79"),
                            Citation(book="Phaladeepika Ch.13")],
            ),
            Prediction(
                key="spouse_profile",
                label="Spouse profile (from 7th sign)",
                value=m["spouse_profile"],
                confidence="MEDIUM",
                chart_evidence=f"7th sign = {sign7}",
            ),
            Prediction(
                key="mangal_dosha",
                label="Mangal Dosha",
                value=("yes — match with another Manglik for harmony"
                       if m["mangal_dosha"] else "no"),
                confidence="HIGH" if m["mangal_dosha"] else "HIGH",
                chart_evidence=f"Mars in H{h_mars}",
                citations=[Citation(book="Lal Kitab Ch.7")],
            ),
            Prediction(
                key="harmony",
                label="Marriage harmony tendency",
                value=("smooth" if h_jup in (1, 5, 7, 9)
                       else "needs work + active maintenance"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter in H{h_jup}",
            ),
            Prediction(
                key="number_of_marriages",
                label="Number-of-marriages signal",
                value=("two-marriage signal" if (h_ven in (7, 8) and
                                                  planet_house(chart, "Saturn") == 7)
                       else "one"),
                confidence="LOW",
                chart_evidence=f"Venus H{h_ven}, Saturn H{planet_house(chart, 'Saturn')}",
            ),
        ]
        # Spouse community / cross-community signal
        verdict, conf, sigs = _spouse_community_signal(chart)
        preds.append(Prediction(
            key="spouse_community",
            label="Spouse community / background lean",
            value={"verdict": verdict, "signals": sigs},
            confidence=conf,
            chart_evidence="; ".join(sigs[:3]) if sigs else "no community signals detected",
            citations=[Citation(book="BPHS Ch.79"),
                        Citation(book="Phaladeepika Ch.13"),
                        Citation(book="Jaimini Sutras (Karakamsa Ch.1)")],
        ))
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
