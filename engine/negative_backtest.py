"""
Negative-sample backtest — sample dasha periods where the engine *would*
flag an event but no documented event of that type happened, to enable
Bayesian P(event | tier) instead of recall-only.

Setup:
    For each known chart and each event type X:
      Positive sample: (md_lord, ad_lord) at the documented event year of X
      Negative sample: (md_lord, ad_lord) at a non-event year (a year where
                       no event of type X is documented)

    Compute:
      P(primary_tier | event=X)   — true positive rate (recall — what we had)
      P(primary_tier | event=¬X)  — false positive rate
      Posterior:
         P(event=X | primary_tier) = P(primary | X) P(X)
                                   / [P(primary|X)P(X) + P(primary|¬X)P(¬X)]

The resulting per-tier posterior is what `engine.calibration` should report
as the calibrated probability for a forecast.

Caveat: "non-event year" only means *not documented*. A real event may have
happened that biographers did not record. We treat documented coverage as
the ground truth — biased toward famous people whose major events ARE
recorded.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random
from dataclasses import dataclass


def _deterministic_seed(s: str) -> int:
    """Stable hash across Python processes (Python's hash() is randomized)."""
    h = hashlib.md5(s.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")

from engine.backtest import (
    EVENT_PATTERNS, _classify, _moon_lon, _birth_dt,
)
from engine.dasha import current_dasha
from engine.known_charts import KNOWN_CHARTS, KnownChart


@dataclass
class TieredCount:
    primary: int = 0
    secondary: int = 0
    miss: int = 0

    @property
    def total(self) -> int:
        return self.primary + self.secondary + self.miss


def _sample_negative_years(
    chart: KnownChart,
    event_type: str,
    n_samples: int = 5,
    seed: int = 42,
) -> list[int]:
    """Pick years from `chart`'s lifespan with NO event of `event_type`."""
    # Lifespan = first event year to last event year
    yrs_with_evt = {ev.year for ev in chart.events if ev.event_type == event_type}
    if not chart.events:
        return []
    span_lo = min(ev.year for ev in chart.events)
    span_hi = max(ev.year for ev in chart.events)
    candidates = [y for y in range(span_lo, span_hi + 1) if y not in yrs_with_evt]
    rng = random.Random(seed + _deterministic_seed(chart.name + event_type) % 10**6)
    rng.shuffle(candidates)
    return candidates[:n_samples]


def run_negative_backtest(n_samples_per_event: int = 5) -> dict:
    """For each event type, count tier matches on positive vs negative years.

    Returns per-event-type:
        positive: TieredCount  — events that happened
        negative: TieredCount  — random non-event years from same chart's life
        precision_primary, recall_primary, posterior_primary
        precision_secondary, posterior_secondary
    """
    pos: dict[str, TieredCount] = {}
    neg: dict[str, TieredCount] = {}

    for chart in KNOWN_CHARTS:
        moon = _moon_lon(chart.birthdata)
        bdt  = _birth_dt(chart.birthdata)
        # Build the fake_chart dict that current_dasha() actually expects
        b = {"year": bdt.year, "month": bdt.month, "day": bdt.day,
             "hour": bdt.hour, "min": bdt.minute}
        fake_chart = {"positions": {"Moon": {"lon": moon, "lon_abs": moon}},
                      "birth": b}

        # ─── Positive samples (events that happened) ───────────────────
        for ev in chart.events:
            pattern = EVENT_PATTERNS.get(ev.event_type)
            if not pattern:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            active = current_dasha(fake_chart, dt.datetime(ev.year, mo, dy))
            md_block = active.get("md")
            ad_block = active.get("ad")
            if md_block is None:
                continue
            md_lord = md_block.get("md") or md_block.get("lord")
            ad_lord = (ad_block.get("ad") or ad_block.get("lord")) if ad_block else None
            md_t = _classify(md_lord, pattern["primary"], pattern["secondary"])
            ad_t = _classify(ad_lord, pattern["primary"], pattern["secondary"])
            best = "primary" if "primary" in (md_t, ad_t) else (
                   "secondary" if "secondary" in (md_t, ad_t) else "miss")
            tc = pos.setdefault(ev.event_type, TieredCount())
            setattr(tc, best, getattr(tc, best) + 1)

        # ─── Negative samples (non-event years) ───────────────────────
        for evt_type in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(chart, evt_type, n_samples_per_event)
            pattern = EVENT_PATTERNS[evt_type]
            for yr in negs:
                active = current_dasha(fake_chart, dt.datetime(yr, 6, 15))
                md_block = active.get("md")
                ad_block = active.get("ad")
                if md_block is None:
                    continue
                md_lord = md_block.get("md") or md_block.get("lord")
                ad_lord = (ad_block.get("ad") or ad_block.get("lord")) if ad_block else None
                md_t = _classify(md_lord, pattern["primary"], pattern["secondary"])
                ad_t = _classify(ad_lord, pattern["primary"], pattern["secondary"])
                best = "primary" if "primary" in (md_t, ad_t) else (
                       "secondary" if "secondary" in (md_t, ad_t) else "miss")
                tc = neg.setdefault(evt_type, TieredCount())
                setattr(tc, best, getattr(tc, best) + 1)

    # ─── Compute precision / posterior per event-type per tier ────────
    summary = {}
    for evt in EVENT_PATTERNS.keys():
        p = pos.get(evt, TieredCount())
        n = neg.get(evt, TieredCount())
        n_pos = p.total
        n_neg = n.total
        if n_pos == 0:
            continue

        # P(tier | event)
        p_pri_given_pos = p.primary / n_pos
        p_sec_given_pos = p.secondary / n_pos
        # P(tier | ¬event)
        p_pri_given_neg = (n.primary / n_neg) if n_neg > 0 else None
        p_sec_given_neg = (n.secondary / n_neg) if n_neg > 0 else None

        # Base rate prior — fraction of years in this chart's documented
        # lifespan where event=X occurred. (Imperfect — see module docstring.)
        # Use the all-charts pooled rate.
        base_rate = n_pos / (n_pos + n_neg) if (n_pos + n_neg) > 0 else 0

        def posterior(tier_pos_rate, tier_neg_rate):
            if tier_neg_rate is None or (tier_pos_rate + tier_neg_rate) == 0:
                return None
            num = tier_pos_rate * base_rate
            den = num + tier_neg_rate * (1 - base_rate)
            return num / den if den > 0 else None

        summary[evt] = {
            "n_positive": n_pos,
            "n_negative": n_neg,
            "base_rate": round(base_rate, 4),
            "positive_tier_dist": {"primary": p.primary, "secondary": p.secondary, "miss": p.miss},
            "negative_tier_dist": {"primary": n.primary, "secondary": n.secondary, "miss": n.miss},
            "P_primary_given_event":  round(p_pri_given_pos, 4),
            "P_primary_given_no_event": round(p_pri_given_neg, 4) if p_pri_given_neg is not None else None,
            "P_secondary_given_event":  round(p_sec_given_pos, 4),
            "P_secondary_given_no_event": round(p_sec_given_neg, 4) if p_sec_given_neg is not None else None,
            # Likelihood ratios — how much more likely is primary tier in
            # an event vs non-event period? >1 = informative, <1 = anti-informative
            "LR_primary":   round(p_pri_given_pos / p_pri_given_neg, 3)
                            if (p_pri_given_neg and p_pri_given_neg > 0) else None,
            "LR_secondary": round(p_sec_given_pos / p_sec_given_neg, 3)
                            if (p_sec_given_neg and p_sec_given_neg > 0) else None,
            # Bayesian posterior: P(event | tier observed) given pooled base rate
            "posterior_event_given_primary":  posterior(p_pri_given_pos, p_pri_given_neg),
            "posterior_event_given_secondary": posterior(p_sec_given_pos, p_sec_given_neg),
        }

    return {
        "n_charts": len(KNOWN_CHARTS),
        "n_samples_per_negative": n_samples_per_event,
        "by_event_type": summary,
    }


def print_report(n_neg: int = 5) -> None:
    r = run_negative_backtest(n_samples_per_event=n_neg)
    print("=" * 96)
    print(f"NEGATIVE-SAMPLE BACKTEST  ({r['n_charts']} charts × {n_neg} negs/event)")
    print("=" * 96)
    print(f"{'event':22s} {'n+':>3s} {'n-':>3s}   {'P(p|+)':>7s} {'P(p|-)':>7s}  "
          f"{'LR_pri':>7s}  {'post(p)':>8s}  {'LR_sec':>7s}")
    for evt, b in sorted(r["by_event_type"].items(),
                         key=lambda x: -(x[1]["LR_primary"] or 0)):
        lr_pri = b["LR_primary"]
        lr_sec = b["LR_secondary"]
        post = b["posterior_event_given_primary"]
        print(f"  {evt:20s} {b['n_positive']:3d} {b['n_negative']:3d}   "
              f"{b['P_primary_given_event']:>6.3f}  "
              f"{b['P_primary_given_no_event'] if b['P_primary_given_no_event'] is not None else 'n/a':>7}  "
              f"{lr_pri if lr_pri is not None else 'inf':>7}  "
              f"{f'{post:.3f}' if post is not None else 'n/a':>8s}  "
              f"{lr_sec if lr_sec is not None else 'inf':>7}")
    print()
    print("LR > 1 => primary-tier signature is informative (raises posterior)")
    print("LR ~ 1 => tier is uninformative (random chance)")
    print("LR < 1 => tier is anti-informative")


if __name__ == "__main__":
    print_report()
