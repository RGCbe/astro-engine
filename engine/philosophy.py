"""
Truth Engine Philosophy
This module stores the foundational philosophical tenets of the engine.
"""

MISSION_STATEMENT = (
    "Our engine does not try to tell people what they want to hear. "
    "It tries to present the strongest conclusions supported by the astrological model, "
    "explains the evidence, acknowledges uncertainty where it exists, "
    "and presents both opportunities and challenges without bias."
)

PRINCIPLES = [
    "Principle 1: Never invent facts.",
    "Principle 2: Never exaggerate certainty.",
    "Principle 3: Never hide strong negative indications.",
    "Principle 4: Never hide strong positive indications.",
    "Principle 5: Always explain *why* a conclusion was reached.",
    "Principle 6: Distinguish between High, Moderate, and Low confidence.",
    "Principle 7: Show both supporting and conflicting evidence before reaching a conclusion."
]

def get_philosophy_text() -> str:
    lines = [f"> **Mission**: {MISSION_STATEMENT}", ""]
    for p in PRINCIPLES:
        lines.append(f"- {p}")
    return "\n".join(lines)
