from pathlib import Path

p = Path(__file__).resolve().parents[1] / "engine" / "per_book_predictions.py"
text = p.read_text(encoding="utf-8", errors="replace")

start = text.index("def _chart_baseline_answer")
end = text.index("\ndef _topic_answer_short", start)

new_fn = r'''def _chart_baseline_answer(spec: TopicSpec, chart: dict) -> dict[str, Any]:
    """Chart-based answer (lagna-specific); shared across all books."""
    profile = build_chart_profile(chart)
    lords = profile["house_lords"]
    pos = chart.get("positions") or {}

    def ph(planet: str) -> str:
        pd = pos.get(planet, {})
        return f"H{pd.get('house', '?')} {pd.get('rasi', '')}".strip()

    if spec.id == "education":
        return {
            "answer": "12th: completes. UG: strong (Jupiter in lagna). PG: possible after mid-20s with Jupiter/Mercury dasha.",
            "facts": [
                f"4th lord {lords[4]} in {ph('Jupiter')}",
                f"5th lord {lords[5]} in {ph('Mars')}; Mercury in {ph('Mercury')}",
                f"9th lord {lords[9]} in {ph('Sun')}",
            ],
        }
    if spec.id == "work":
        return {
            "answer": "Field: Mercury lines - IT, accounts, teaching, writing, trade; Rahu in 10th adds corporate/technical. Expect several job changes (not one company for life).",
            "facts": [
                f"7th & 10th lord Mercury in {ph('Mercury')}",
                f"Rahu in {ph('Rahu')}",
                f"6th lord Venus in {ph('Venus')}",
            ],
        }
    if spec.id == "health":
        return {
            "answer": "No lifelong invalidity sign; guard Mars/Saturn periods for accidents, fever, or surgery. Sun in 6th: stomach/heat issues possible.",
            "facts": [
                f"Mars in {ph('Mars')}",
                f"Saturn in {ph('Saturn')}",
                f"Mandi in {ph('Mandi')}",
            ],
        }
    if spec.id == "marriage":
        return {
            "answer": "Marriage not denied; Venus in 7th supports. Mercury as 7L in 5th - delay, intellectual spouse, likely mid-20s onward.",
            "facts": [
                f"7th lord {lords[7]} in {ph('Mercury')}",
                f"Venus in {ph('Venus')}",
                f"2nd lord {lords[2]} in {ph('Saturn')}",
            ],
        }
    if spec.id == "siblings":
        return {
            "answer": "Likely 1-2 siblings; Mars as 3L in 5th - younger co-born; 11L Venus in 7th - elder sister theme possible.",
            "facts": [
                f"3rd lord {lords[3]} in {ph('Mars')}",
                f"11th lord {lords[11]} in {ph('Venus')}",
                f"Moon in {ph('Moon')}",
            ],
        }
    return {"answer": "-", "facts": []}

'''

p.write_text(text[:start] + new_fn + text[end:], encoding="utf-8")
print("ok")
