"""
Remedy engine — for every detected affliction, prescribe concrete remedies.

Per the engine's mission: bad-finder → remedy-giver. The bad findings drive
the remedy prescriptions.

Three remedy categories per affliction:
    1. Lal Kitab: charity, behavior, symbolic acts (no cost)
    2. Vedic / Mantra: mantras, yantras, deities (Sanskrit)
    3. Behavioral: real-world action (relationship/lifestyle change)
    4. Gemstone (with mandatory caveat: requires shadbala check)
    5. Timing: weekday, transit window, muhurta if applicable

API:
    remedies_for(affliction) → list[Remedy]
    remedies_for_chart(chart) → comprehensive remedy plan
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.afflictions import Affliction, detect_all


@dataclass
class Remedy:
    affliction_code: str
    type: str          # "lal_kitab" | "vedic_mantra" | "behavioral" |
                       # "gemstone_with_caveat" | "timing" | "donation"
    action: str
    when: str = ""     # e.g. "Saturdays", "Rahu kala", "Amavasya"
    duration: str = ""  # e.g. "40 days continuous", "lifetime", "until afflicted MD ends"
    caveat: str = ""    # warnings (e.g. gemstone disclaimers)


# ─── Remedy tables per affliction code ─────────────────────────────────────
REMEDY_TABLE: dict[str, list[dict]] = {
    "MANGAL_DOSHA": [
        {"type": "vedic_mantra",  "action": "Chant Hanuman Chalisa daily", "when": "Tuesday + Saturday morning", "duration": "108 days minimum"},
        {"type": "vedic_mantra",  "action": "Recite Mangal Beej Mantra (Om Kram Kreem Kraum Sah Bhaumaya Namah)", "when": "Tuesday before sunrise", "duration": "21 mala / day for 40 days"},
        {"type": "lal_kitab",     "action": "Donate red lentils (masoor dal) and jaggery to Hanuman temple", "when": "Tuesday"},
        {"type": "behavioral",    "action": "Avoid red-colored food and alcohol on Tuesdays. Practice patience in marital disputes — DO NOT raise voice."},
        {"type": "donation",      "action": "Feed unmarried girls or widows with sweet rice", "when": "any Tuesday"},
        {"type": "gemstone_with_caveat", "action": "Coral (moonga) — only if Mars is functional malefic and shadbala-strong. NOT recommended without astrologer + shadbala verification.", "caveat": "Gemstones must NEVER be worn for debilitated or 6/8/12-placed Mars."},
        {"type": "behavioral",    "action": "Marry someone with same Mangal dosha, OR perform Kumbh Vivaha with Vishnu icon before marriage."},
    ],
    "KAL_SARP": [
        {"type": "vedic_mantra",  "action": "Recite Maha Mrityunjaya Mantra (Om Tryambakam Yajamahe...)", "when": "daily morning", "duration": "108 times daily for 40 days"},
        {"type": "vedic_mantra",  "action": "Worship Naga Devata at a Shiva temple", "when": "Naga Panchami + every Amavasya"},
        {"type": "lal_kitab",     "action": "Float coconut + black sesame seeds in flowing water (river/sea)", "when": "Amavasya"},
        {"type": "behavioral",    "action": "Never harm snakes; donate towards snake-bite hospitals or wildlife reserves."},
        {"type": "donation",      "action": "Donate at Kalahasti, Trimbakeshwar, or any Naga temple. Ideally perform Kala Sarpa Dosha Nivarana puja there."},
        {"type": "vedic_mantra",  "action": "Chant Rahu Beej Mantra (Om Bhram Bhreem Bhraum Sah Rahave Namah) and Ketu Beej Mantra alternating days."},
    ],
    "KEMADRUMA": [
        {"type": "vedic_mantra",  "action": "Chant Chandra Beej Mantra (Om Shram Shreem Shraum Sah Chandraya Namah)", "when": "Monday morning", "duration": "108x daily for 40 days"},
        {"type": "lal_kitab",     "action": "Donate milk, white rice, and white cloth to elderly women on Mondays"},
        {"type": "behavioral",    "action": "Take care of mother actively — daily phone call minimum, never speak harshly. Foster strong female friendships."},
        {"type": "behavioral",    "action": "Drink water from a silver vessel. Wear white on Mondays."},
        {"type": "vedic_mantra",  "action": "Worship Shiva (consort of Moon) — chant Om Namah Shivaya 108 times daily"},
        {"type": "donation",      "action": "Feed cows on full moon (Purnima) — milk, sugar, white pumpkin"},
    ],
    "PITRU_DOSHA": [
        {"type": "vedic_mantra",  "action": "Perform Pitru Tarpan during Pitru Paksha (waning moon Sept-Oct annually)", "when": "Pitru Paksha", "duration": "all 16 days"},
        {"type": "vedic_mantra",  "action": "Recite Pitru Stotra and Vishnu Sahasranama daily", "duration": "lifetime habit"},
        {"type": "behavioral",    "action": "Serve father (and father-figures) with respect. Never disrespect ancestors verbally or in action."},
        {"type": "donation",      "action": "Donate wheat, jaggery, and copper to Brahmin priests on Sunday"},
        {"type": "lal_kitab",     "action": "Offer water to peepal tree daily for 43 days. Light mustard-oil lamp under it on Saturday."},
        {"type": "vedic_mantra",  "action": "Visit Gaya (Bihar) once for Pitru Tarpan if possible — considered the supreme remedy."},
    ],
    "GRAHAN_DOSHA": [
        {"type": "vedic_mantra",  "action": "Maha Mrityunjaya Mantra 108 times daily during eclipses; bathe and donate after every solar/lunar eclipse"},
        {"type": "lal_kitab",     "action": "Donate silver and rice during eclipse periods"},
        {"type": "behavioral",    "action": "Do not start new ventures during eclipse periods. Fast on eclipse days if possible."},
        {"type": "vedic_mantra",  "action": "Chant Surya/Chandra mantra alternating, plus Rahu/Ketu beej mantra"},
    ],
    "GURU_CHANDALA": [
        {"type": "vedic_mantra",  "action": "Chant Guru Beej Mantra (Om Gram Greem Graum Sah Gurave Namah) daily", "when": "Thursday morning"},
        {"type": "behavioral",    "action": "Respect spiritual teachers, parents, elders. Never deceive in matters of religion or wisdom."},
        {"type": "donation",      "action": "Donate yellow items (turmeric, gram dal, banana) to a Brahmin priest on Thursday"},
        {"type": "vedic_mantra",  "action": "Recite Vishnu Sahasranama on Thursdays"},
        {"type": "lal_kitab",     "action": "Apply turmeric or saffron tilak on forehead. Avoid alcohol and meat."},
    ],
    "VISH_YOGA": [
        {"type": "vedic_mantra",  "action": "Maha Mrityunjaya Mantra 108x daily", "duration": "until next dasha shift"},
        {"type": "lal_kitab",     "action": "Donate mustard oil and iron on Saturdays"},
        {"type": "behavioral",    "action": "Practice meditation daily for 20+ min. Address depression seriously — therapy is part of remedy."},
        {"type": "vedic_mantra",  "action": "Worship Lord Shiva — Lingam abhishekam with milk on Mondays and Saturdays"},
    ],
    "DARIDRA_YOGA": [
        {"type": "vedic_mantra",  "action": "Sri Sukta recitation daily", "duration": "108 days"},
        {"type": "lal_kitab",     "action": "Donate to women on Fridays — sweets, white items"},
        {"type": "behavioral",    "action": "Track expenses ruthlessly. Avoid debt. Never lend to people who don't return."},
        {"type": "vedic_mantra",  "action": "Worship Lakshmi Narayana on Friday + full moon"},
        {"type": "donation",      "action": "Feed poor or homeless on Fridays"},
    ],
    # ─── Lal Kitab rins ────────────────────────────────────────────────
    "RIN_PITRA_RIN": [
        {"type": "vedic_mantra",  "action": "Pitru Tarpan during Pitru Paksha"},
        {"type": "behavioral",    "action": "Never lie, cheat, or harm friends/brothers. Avoid extramarital affairs."},
        {"type": "lal_kitab",     "action": "Offer water + black sesame to peepal tree daily for 43 days"},
        {"type": "donation",      "action": "Donate wheat, jaggery, copper at temple on Sunday"},
    ],
    "RIN_MATRA_RIN": [
        {"type": "behavioral",    "action": "Serve mother actively. Never raise voice against mother or any woman."},
        {"type": "donation",      "action": "Donate silver, rice, milk to elderly women on Monday"},
        {"type": "lal_kitab",     "action": "Offer water at any sacred river (Ganga ideally) on Mondays"},
        {"type": "vedic_mantra",  "action": "Chandra Beej Mantra + Durga Saptashati"},
    ],
    "RIN_BHRATRA_RIN": [
        {"type": "behavioral",    "action": "Maintain harmony with brothers and male cousins; help when in need without being asked."},
        {"type": "donation",      "action": "Donate red lentils, sweets to younger boys on Tuesday"},
        {"type": "lal_kitab",     "action": "Avoid jealousy; never speak ill of siblings"},
    ],
    "RIN_STREE_RIN": [
        {"type": "behavioral",    "action": "Treat spouse and all women with respect. Never insult women publicly or privately."},
        {"type": "donation",      "action": "Donate white items (rice, milk, sugar, white cloth) on Friday"},
        {"type": "vedic_mantra",  "action": "Worship Lakshmi or Durga on Fridays"},
        {"type": "lal_kitab",     "action": "Avoid extramarital relationships. Be faithful in word and deed."},
    ],
    "RIN_PUTRA_RIN": [
        {"type": "behavioral",    "action": "Respect children — your own and others'. Never abuse or neglect."},
        {"type": "donation",      "action": "Donate yellow items (turmeric, banana, gram dal) to Brahmins on Thursday"},
        {"type": "vedic_mantra",  "action": "Vishnu Sahasranama parayanam; Santan Gopal mantra if seeking children"},
        {"type": "behavioral",    "action": "Serve cows; feed Brahmins; perform Putra-Kameshti yagna under guidance if desperate for children"},
    ],
}


# Generic remedies per planet (for combust/debilitated/afflicted planets)
PLANET_GENERIC_REMEDIES = {
    "Sun": [
        {"type": "vedic_mantra", "action": "Surya Namaskar 12 rounds at sunrise", "when": "Sunday + daily"},
        {"type": "vedic_mantra", "action": "Aditya Hridayam Stotra recitation", "when": "Sunday"},
        {"type": "lal_kitab", "action": "Offer water (arghya) to Sun at sunrise daily"},
        {"type": "donation", "action": "Donate wheat, jaggery, copper, ruby on Sunday"},
        {"type": "behavioral", "action": "Respect father, government officials, authority figures"},
    ],
    "Moon": [
        {"type": "vedic_mantra", "action": "Chandra Beej Mantra 108x", "when": "Monday morning"},
        {"type": "lal_kitab", "action": "Drink water from silver vessel"},
        {"type": "donation", "action": "Donate milk, rice, white cloth on Monday"},
        {"type": "behavioral", "action": "Respect mother and women; nurture mental health actively"},
    ],
    "Mars": [
        {"type": "vedic_mantra", "action": "Hanuman Chalisa daily", "when": "Tuesday + Saturday"},
        {"type": "lal_kitab", "action": "Donate red lentils, jaggery on Tuesday"},
        {"type": "behavioral", "action": "Practice anger control; exercise physically; avoid red meat"},
    ],
    "Mercury": [
        {"type": "vedic_mantra", "action": "Vishnu Sahasranama daily; Buddha Stotra on Wednesday"},
        {"type": "behavioral", "action": "NEVER lie. Speak truthfully even when costly."},
        {"type": "lal_kitab", "action": "Feed parrots; donate green moong dal on Wednesday"},
        {"type": "donation", "action": "Donate green items, stationery, books to students"},
    ],
    "Jupiter": [
        {"type": "vedic_mantra", "action": "Guru Beej Mantra; Vishnu Sahasranama on Thursday"},
        {"type": "lal_kitab", "action": "Apply saffron tilak; donate turmeric on Thursday"},
        {"type": "behavioral", "action": "Respect teachers, gurus, elders. Pursue knowledge actively."},
        {"type": "donation", "action": "Donate yellow items, gram dal, banana to Brahmin priests"},
    ],
    "Venus": [
        {"type": "vedic_mantra", "action": "Sri Sukta + Lakshmi Stotra on Friday"},
        {"type": "lal_kitab", "action": "Donate white items (rice, sugar, milk, white cloth) on Friday"},
        {"type": "behavioral", "action": "Respect women. Cultivate art, music, beauty in daily life."},
    ],
    "Saturn": [
        {"type": "vedic_mantra", "action": "Hanuman Chalisa on Saturday; Shani Stotra"},
        {"type": "lal_kitab", "action": "Light mustard-oil lamp under peepal tree on Saturday"},
        {"type": "donation", "action": "Donate black items (sesame, iron, black cloth) to elderly poor on Saturday"},
        {"type": "behavioral", "action": "Serve elders, laborers, the marginalized. Practice patience."},
    ],
    "Rahu": [
        {"type": "vedic_mantra", "action": "Rahu Beej Mantra; Durga Saptashati"},
        {"type": "lal_kitab", "action": "Donate barley (jau) to flowing water; feed crows"},
        {"type": "behavioral", "action": "Avoid manipulation, deceit, shortcuts. Stay grounded."},
    ],
    "Ketu": [
        {"type": "vedic_mantra", "action": "Ketu Beej Mantra; Ganesha Atharvashirsha"},
        {"type": "lal_kitab", "action": "Feed dogs (especially street dogs); donate black-and-white items"},
        {"type": "behavioral", "action": "Cultivate spiritual practice. Don't suppress detachment urges."},
    ],
}


def remedies_for(affliction: Affliction) -> list[Remedy]:
    """Look up remedies for a single affliction."""
    out: list[Remedy] = []
    rec = REMEDY_TABLE.get(affliction.code, [])
    for r in rec:
        out.append(Remedy(
            affliction_code=affliction.code,
            type=r["type"], action=r["action"],
            when=r.get("when", ""), duration=r.get("duration", ""),
            caveat=r.get("caveat", ""),
        ))

    # If it's a planet-specific affliction (combust, debilitated), add planet remedies
    if affliction.code.startswith(("COMBUST_", "DEBIL_")):
        planet = affliction.code.split("_", 1)[1].title()
        for r in PLANET_GENERIC_REMEDIES.get(planet, []):
            out.append(Remedy(
                affliction_code=affliction.code,
                type=r["type"], action=r["action"],
                when=r.get("when", ""), duration=r.get("duration", ""),
            ))
    return out


def remedies_for_chart(chart) -> dict:
    """Comprehensive remedy plan for ALL detected afflictions in the chart."""
    afflictions = detect_all(chart)
    plan = {
        "n_afflictions_detected": len(afflictions),
        "engine_mission": ("Bad-finder + remedy-giver. Every detected "
                           "affliction below has corresponding remedies. "
                           "Per truth directive, NO finding is softened."),
        "afflictions_with_remedies": [],
    }
    seen_remedies = set()  # dedupe across afflictions
    for a in afflictions:
        rems = remedies_for(a)
        rem_records = []
        for r in rems:
            key = (r.type, r.action)
            if key in seen_remedies:
                continue
            seen_remedies.add(key)
            rem_records.append({
                "type": r.type, "action": r.action,
                "when": r.when, "duration": r.duration, "caveat": r.caveat,
            })
        plan["afflictions_with_remedies"].append({
            "affliction": {
                "code": a.code, "name": a.name, "severity": a.severity,
                "category": a.category, "evidence": a.evidence,
                "source": a.classical_source, "description": a.description,
                "affected": list(a.affected),
            },
            "remedies": rem_records,
        })

    # Also add a "weakest planets — generic remedies" section
    if hasattr(chart, "bala_summary"):
        plan["weakest_planets_generic_remedies"] = []
        for p in chart.bala_summary.get("weakest", [])[:3]:
            rems = []
            for r in PLANET_GENERIC_REMEDIES.get(p, []):
                rems.append({"type": r["type"], "action": r["action"], "when": r.get("when", "")})
            plan["weakest_planets_generic_remedies"].append({
                "planet": p, "remedies": rems
            })

    return plan
