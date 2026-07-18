"""Sade Sati Detector — 7.5 year Saturn cycle through 12th/1st/2nd from natal Moon.

Source: BPHS, Phaladeepika, Sarvarth Chintamani.
This is the classical Vedic Saturn cycle (different from Western 'Saturn Return').
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from transit_engine import transit_positions

from vedic_core import RASIS  # canonical 12 signs


def compute_sade_sati_periods(chart, years_horizon=80):
    """Compute all Sade Sati phases from birth onwards.

    Phases:
      - 'Phase 1 (Rising)' — Saturn in 12th from natal Moon (~2.5 years)
      - 'Phase 2 (Peak)'   — Saturn ON natal Moon sign (~2.5 years)
      - 'Phase 3 (Setting)' — Saturn in 2nd from natal Moon (~2.5 years)
    """
    pos = chart["positions"]
    moon_rasi_idx = pos["Moon"]["rasi_idx"]
    sade_sati_signs = [
        ((moon_rasi_idx - 1) % 12, "Phase 1 (Rising / 12th from Moon)"),
        (moon_rasi_idx, "Phase 2 (Peak / On Moon sign)"),
        ((moon_rasi_idx + 1) % 12, "Phase 3 (Setting / 2nd from Moon)"),
    ]

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])
    end_horizon = birth_dt + dt.timedelta(days=years_horizon * 365.25)

    # Sample every 7 days, find when transit Saturn enters/leaves each sign
    periods = []
    cur_phase = None
    cur_start = None

    d = birth_dt
    while d <= end_horizon:
        try:
            tr = transit_positions(d)
            sat_ri = tr["Saturn"]["rasi_idx"]
        except Exception:
            d += dt.timedelta(days=7)
            continue

        # Which Sade Sati phase (if any)?
        in_phase = None
        for phase_ri, phase_name in sade_sati_signs:
            if sat_ri == phase_ri:
                in_phase = phase_name
                break

        if in_phase != cur_phase:
            # Phase boundary
            if cur_phase is not None and cur_start is not None:
                periods.append({
                    "phase": cur_phase,
                    "start": cur_start,
                    "end": d,
                    "duration_days": (d - cur_start).days,
                })
            cur_phase = in_phase
            cur_start = d if in_phase else None

        d += dt.timedelta(days=7)

    if cur_phase and cur_start:
        periods.append({
            "phase": cur_phase,
            "start": cur_start,
            "end": d,
            "duration_days": (d - cur_start).days,
        })

    return periods


def sade_sati_summary(chart):
    """Show Sade Sati timeline."""
    periods = compute_sade_sati_periods(chart, years_horizon=80)
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"])
    today = dt.datetime.now()

    if not periods:
        return "No Sade Sati periods detected in 80-year horizon."

    lines = [f"=== SADE SATI TIMELINE FOR {chart['name'].upper()} ==="]
    lines.append(f"Natal Moon: {chart['moon_rasi']}\n")

    for p in periods:
        age_at_start = (p["start"] - birth_dt).days / 365.25
        is_now = p["start"] <= today <= p["end"]
        marker = " ★ CURRENT" if is_now else " (past)" if p["end"] < today else " (future)"
        years = p["duration_days"] / 365.25
        lines.append(f"  Age {age_at_start:5.1f}: {p['phase']:45s}  {p['start'].strftime('%b %Y')} - {p['end'].strftime('%b %Y')} ({years:.1f}y){marker}")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(sade_sati_summary(chart))
