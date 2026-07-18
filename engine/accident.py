"""
Accident / health-crisis pattern detector.

Surfaces the chart's signature for sudden injury, surgery, vehicle
accident, fall, fire, or chronic illness — and names the windows when
those signatures peak.

Vedic principles applied:
    - Mars in 4/8/12 + Saturn aspect → vehicle / fall risk
    - Rahu in 4/8/12 → unexpected, foreign, electric / chemical
    - Mars-Saturn together / aspecting → surgery, sharp injury
    - Mars-Rahu together → fire, explosion, sudden trauma
    - 6th lord + 8th lord interaction → chronic illness
    - Marana Karaka Sthana for malefics → severe placement
    - Body part = nakshatra of the malefic (Kalapurusha mapping)

Output: list of detected patterns + name + estimated severity +
the dasha windows when MD or AD lord matches the malefic in question.
"""
from __future__ import annotations

from dataclasses import dataclass


# Body parts ruled by each nakshatra (Kalapurusha — abbreviated)
NAKSHATRA_BODY = {
    "Ashvini": "head, brain, knees",
    "Bharani": "feet, soles",
    "Krittika": "head, eyebrows",
    "Rohini": "forehead, eyes, nose",
    "Mrigashirsha": "eyes, sinus",
    "Ardra": "hair, eyes",
    "Punarvasu": "fingers, nose",
    "Pushya": "mouth, face",
    "Ashlesha": "ears, joints, nails",
    "Magha": "lips, chin, nose",
    "Purva Phalguni": "right hand, lips",
    "Uttara Phalguni": "left hand",
    "Hasta": "hands, fingers",
    "Chitra": "neck, forehead",
    "Swati": "chest, abdomen",
    "Vishakha": "lower abdomen, hips",
    "Anuradha": "stomach, breast",
    "Jyeshtha": "right side, ribs",
    "Mula": "left side, hips, sciatic nerve",
    "Purva Ashadha": "thighs, back",
    "Uttara Ashadha": "thighs, waist",
    "Shravana": "ears, organs of hearing",
    "Dhanishta": "back, legs",
    "Shatabhisha": "jaw, knees",
    "Purva Bhadrapada": "ribs, sides",
    "Uttara Bhadrapada": "feet, calves",
    "Revati": "abdomen, feet, ankles",
}


@dataclass
class AccidentPattern:
    name: str
    nature: str
    body_part: str
    severity: str       # HIGH | MEDIUM | LOW
    evidence: str
    classical_source: str
    peak_dashas: list[str]   # Mahadasha lords during which risk peaks


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    lagna_sign = int(chart.lagna_lon // 30)
    return ((int(lon // 30) - lagna_sign) % 12) + 1


def _planet_nakshatra(chart, planet: str) -> str:
    return (chart.nakshatras or {}).get(planet, {}).get("name", "")


def detect_accident_patterns(chart) -> list[AccidentPattern]:
    out: list[AccidentPattern] = []

    h_mars = _planet_house(chart, "Mars")
    h_sat = _planet_house(chart, "Saturn")
    h_rahu = _planet_house(chart, "Rahu")
    h_ketu = _planet_house(chart, "Ketu")

    nak_mars = _planet_nakshatra(chart, "Mars")
    nak_sat = _planet_nakshatra(chart, "Saturn")

    # 1. Mars in 4/8/12
    if h_mars in (6, 8, 12):
        body = NAKSHATRA_BODY.get(nak_mars, "extremities")
        out.append(AccidentPattern(
            name="Mars in dusthana from lagna",
            nature="Sudden injury, cuts, burns, accidents, surgery",
            body_part=body,
            severity="MEDIUM",
            evidence=f"Mars sits in H{h_mars} (dusthana) — Mars's "
                     f"nakshatra is {nak_mars}, which rules {body}.",
            classical_source="Phaladeepika; BPHS Ch.32",
            peak_dashas=["Mars", "Ketu", "Rahu", "Saturn"],
        ))

    # 2. Saturn in 4/8/12
    if h_sat in (6, 8, 12):
        body = NAKSHATRA_BODY.get(nak_sat, "joints, bones, knees")
        out.append(AccidentPattern(
            name="Saturn in dusthana from lagna",
            nature="Chronic illness, fall, fracture, slow-developing health issue",
            body_part=body,
            severity="MEDIUM",
            evidence=f"Saturn sits in H{h_sat} (dusthana) — its "
                     f"nakshatra is {nak_sat}, ruling {body}.",
            classical_source="Phaladeepika; Saravali Ch.43",
            peak_dashas=["Saturn", "Rahu", "Ketu"],
        ))

    # 3. Rahu in 4/8/12
    if h_rahu in (6, 8, 12):
        out.append(AccidentPattern(
            name="Rahu in dusthana",
            nature="Unexpected accident, electrical or chemical hazard, poisoning",
            body_part="nervous system, skin, blood",
            severity="MEDIUM",
            evidence=f"Rahu sits in H{h_rahu} (dusthana).",
            classical_source="BPHS Ch.32; Lal Kitab Ch.5",
            peak_dashas=["Rahu", "Saturn", "Mars"],
        ))

    # 4. Mars-Saturn conjunct or 7th-aspect
    sign_mars = int(chart.positions.get("Mars", 0) // 30)
    sign_sat = int(chart.positions.get("Saturn", 0) // 30)
    diff = (sign_mars - sign_sat) % 12
    if diff == 0 or diff == 6:
        out.append(AccidentPattern(
            name="Mars-Saturn conjunction or opposition",
            nature="Surgery, sharp-instrument injury, mechanical accident",
            body_part="bone, joint, lower body",
            severity="HIGH" if diff == 0 else "MEDIUM",
            evidence=f"Mars and Saturn are {'conjunct' if diff == 0 else 'opposite'} — "
                     "classical 'Bhasma-Krura' contact.",
            classical_source="BPHS Ch.86; Phaladeepika Ch.6",
            peak_dashas=["Mars", "Saturn", "Rahu"],
        ))

    # 5. Mars-Rahu conjunction → Angarak (fire / explosion)
    sign_rahu = int(chart.positions.get("Rahu", 0) // 30)
    if (sign_mars - sign_rahu) % 12 == 0:
        out.append(AccidentPattern(
            name="Angarak Yoga (Mars-Rahu)",
            nature="Fire, explosion, sudden violent trauma, accident",
            body_part="head, blood, skin",
            severity="HIGH",
            evidence="Mars and Rahu are in the same sign — Angarak Yoga.",
            classical_source="Lal Kitab Ch.7; BPHS Ch.36",
            peak_dashas=["Mars", "Rahu"],
        ))

    # 6. 6th-lord and 8th-lord interaction (chronic illness)
    SIGN_LORD = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
                 5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
                 9: "Saturn", 10: "Saturn", 11: "Jupiter"}
    lagna = int(chart.lagna_lon // 30)
    l6 = SIGN_LORD[(lagna + 5) % 12]
    l8 = SIGN_LORD[(lagna + 7) % 12]
    sign_l6 = int(chart.positions.get(l6, 0) // 30)
    sign_l8 = int(chart.positions.get(l8, 0) // 30)
    if (sign_l6 - sign_l8) % 12 == 0:
        out.append(AccidentPattern(
            name="6th-lord ↔ 8th-lord conjunction",
            nature="Chronic disease, recurring health issue",
            body_part="depends on the lords' nakshatras",
            severity="MEDIUM",
            evidence=f"6th-lord ({l6}) and 8th-lord ({l8}) share a sign.",
            classical_source="BPHS Ch.30",
            peak_dashas=[l6, l8],
        ))

    # 7. Marana Karaka Sthana for Mars (in 7th)
    if h_mars == 7:
        out.append(AccidentPattern(
            name="Mars in Marana Karaka Sthana (H7)",
            nature="Marriage discord, partnership injury",
            body_part="lower abdomen",
            severity="MEDIUM",
            evidence="Mars sits in its death-place (H7) — Marana Karaka Sthana.",
            classical_source="Phaladeepika; Jaimini Sutras",
            peak_dashas=["Mars", "Venus"],
        ))

    return out


def render_accident_markdown(chart) -> str:
    out = ["## ✦ Health & Accident Signatures (with peak windows)\n"]
    pats = detect_accident_patterns(chart)
    if not pats:
        out.append(
            "Your chart shows no major classical accident-pattern. Standard "
            "caution still applies in periods when malefics transit your "
            "lagna or 8th house."
        )
        return "\n".join(out)
    out.append(
        "The classical texts identify several signatures that mark "
        "elevated risk for sudden injury, surgery, or chronic illness. "
        "If you have already lived through one of these, you will "
        "recognise the pattern. Each entry names the *peak dasha periods* "
        "when that pattern is most active — that is when extra caution, "
        "the verbatim remedies given earlier, and avoidance of risk "
        "behaviour matter most."
    )
    out.append("")
    for p in pats:
        sev_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪"}[p.severity]
        out.append(f"### {sev_color} {p.name}")
        out.append("")
        out.append(f"**Likely nature:** {p.nature}")
        out.append("")
        out.append(f"**Body part most exposed:** {p.body_part}")
        out.append("")
        out.append(f"**Why the chart shows this:** {p.evidence}")
        out.append("")
        out.append(f"**Peak windows:** during the dashas of "
                   f"**{', '.join(p.peak_dashas)}** (especially when both "
                   "MD and AD lords are in this list).")
        out.append("")
        out.append(f"*— Classical source: {p.classical_source}.*")
        out.append("")
    out.append(
        "*Reminder: the chart shows the *predisposition*, not the "
        "verdict. Disciplined behaviour, the verbatim remedies given "
        "earlier, and seasonal medical check-ups during peak dashas "
        "shift the outcome.*"
    )
    return "\n".join(out)
