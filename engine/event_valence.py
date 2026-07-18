"""Infer expected auspicious/inauspicious from known-event text (for strict accuracy scoring)."""


def infer_event_valence(event_text: str, category: str = "") -> str:
    text = (event_text or "").lower()
    if any(w in text for w in (
        "flop", "failed", "failure", "setback", "died", "death", "injury",
        "hospital", "bankrupt", "debt", "loss", "misfortune", "assassinated",
        "assassination", "widowhood", "heart attack", "passed away",
    )):
        return "inauspicious"
    if any(w in text for w in (
        "blockbuster", "mega-hit", "hit", "breakthrough", "married", "born",
        "award", "honor", "bought", "founded", "record", "won", "debut",
        "sworn in", "re-elected", "elected", "chief minister", "prime minister",
        "bharat ratna", "padma", "invested", "inherited", "moved into",
        "sailed", "returned", "gave birth", "son born", "daughter born",
    )):
        return "auspicious"
    if category in ("wealth_loss", "health", "father", "mother", "death_self"):
        return "inauspicious"
    if category in ("marriage", "children", "honor", "wealth", "property"):
        return "auspicious"
    return "neutral"
