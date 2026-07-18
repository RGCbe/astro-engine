# Antigravity Handoff — Option C Continuation Roadmap

**Date:** 2026-05-26 (updated for parallel-work mode)
**Origin:** Claude session, Phase 1 complete (30 new event functions added).
**For:** Antigravity working in **PARALLEL** with Claude.

This document tells you exactly **where things stand, what's done, what's next, and how to add functions without breaking anything**.

---

## ⚡ PARALLEL WORK MODE — IMPORTANT

**As of 2026-05-26, Claude and Antigravity work simultaneously.** Read these THREE files first:

1. **`COORDINATION_PROTOCOL.md`** — file ownership zones, lock mechanism, conflict resolution
2. **`STATUS.md`** — live activity log (both AIs append here)
3. **`SYNC_LOG.md`** — VPS sync history (both AIs log every push)

**Quick rule:**
- 🤖 **Claude** owns the OLD engine (`event_predictor_v2.py` and friends — rule-based)
- 🚀 **Antigravity** owns the NEW engine (`scratch/optimize_*.py` + `astro_numerology_weights.json` — optimized GAC)
- `_battle_vijay.py` is the only shared engine file (OLD section + NEW section by function)

Before editing a shared file, set a lock:
```bash
touch F:/astro/.lock_<filename>_<ai_name>
# ... do work ...
rm F:/astro/.lock_<filename>_<ai_name>
```

---

## ✅ Phase 1 Status (COMPLETE)

Built **30 new event_* functions** in `F:/astro/runtime/event_predictor_v2.py`:

1. event_siblings (3H)
2. event_vehicle_purchase (4H)
3. event_business_start (10H)
4. event_promotion (10H)
5. event_legal_dispute (6H)
6. event_inheritance (8H)
7. event_speculation_gain (5H/11H)
8. event_speculation_loss (5H)
9. event_in_law_event (7H/2H)
10. event_friend_loss (11H)
11. event_partnership_formation (7H)
12. event_partnership_break (7H)
13. event_pet_acquisition (6H)
14. event_charity_donation (12H)
15. event_visa_grant (9H/12H)
16. event_eclipse_impact (Transit)
17. event_saturn_return (Transit)
18. event_jupiter_return (Transit)
19. event_pregnancy (5H)
20. event_engagement (7H)
21. event_book_publication (9H/3H)
22. event_award_nomination (11H)
23. event_house_construction (4H)
24. event_grandchildren_birth (9H)
25. event_brand_endorsement (11H)
26. event_political_office (10H)
27. event_jail_confinement (12H)
28. event_tax_dispute (6H)
29. event_voice_career (2H)
30. event_retirement (10H/12H)

**ALL_PATTERNS_V2 count: 17 → 47**
**Accuracy regression check: PASSED (80.3% steady)**
**Vijay battle: 86% steady**

---

## 🎯 What's Left — Phase 2 through Phase 10 (~224 more categories)

Refer to `F:/astro/ATRO_FULL_CATEGORY_LIST.md` and `.pdf` for the FULL inventory.
Each remaining category from the "❌ Missing" column needs a new function.

### Phase 2 (Next 30 — Body/Health expansion)
- event_birth_circumstances (1H — C-section / premature)
- event_personality_shift (1H — identity reinvention)
- event_charisma_peak (1H — leadership rise)
- event_voice_loss (2H — laryngitis, throat surgery)
- event_dental_event (2H — tooth loss, dental surgery)
- event_eye_problem (2H right eye, 12H left eye)
- event_diet_change (2H — fasting cycles)
- event_sibling_marriage (3H — separate from generic sibling)
- event_sibling_death (3H)
- event_hand_arm_injury (3H)
- event_hearing_issue (3H/11H)
- event_sports_milestone (3H — Mars in 3H + Sun)
- event_writing_career (3H/Mercury)
- event_home_renovation (4H — separate from purchase)
- event_real_estate_dispute (4H + 6H combo)
- event_move_new_city (4H+12H)
- event_school_admission_child (5H — own children's school)
- event_romance_affair (5H + Venus + Rahu)
- event_first_love (5H + Venus first activation)
- event_mantra_siddhi (5H + Jupiter + Ketu)
- event_creative_breakthrough (5H — composer/artist)
- event_devotion_intensify (5H + Jupiter + Ketu)
- event_surgery_major (6H + 8H + Mars)
- event_lawsuit_won (6H + Mars favorable)
- event_lawsuit_lost (6H + Saturn affliction)
- event_workplace_conflict (6H + 10H)
- event_marriage_arranged (7H + Mercury MD)
- event_marriage_love (7H + Venus + Mars)
- event_second_marriage (7H + 2nd 7L period)
- event_spouse_health_crisis (7H + 8H from 7H = 2H)

### Phase 3 (Next 30 — Wealth/Finance/Property)
- event_lottery_win (5H + 11H + Rahu)
- event_lottery_loss (5H + 12H)
- event_inheritance_land (4H + 8H)
- event_insurance_claim (8H + Saturn)
- event_business_expansion (10H + 11H)
- event_business_closure (10L + 12L)
- event_income_breakthrough (2L + 11L)
- event_salary_raise (10L + 2L)
- event_salary_cut (10L + 12L)
- event_loan_approval (6L + Venus)
- event_loan_default (6L + Saturn)
- event_debt_freedom (6L exits dasha + Jupiter)
- event_franchise_open (10L + 11L + Rahu)
- event_patent_grant (5H + 11H)
- event_royalty_payment (5H + 11H + Mercury)
- event_sponsorship_deal (11H + Venus)
- event_subscriber_milestone (11H + Rahu)
- event_share_purchase (5H + 11H Mercury)
- event_share_sale (2H + 5H)
- event_stock_crash_hit (5H + Saturn aspect)
- event_crypto_gain (Rahu + 5H + 11H)
- event_crypto_loss (Rahu + 5H + Ketu)
- event_bonus_windfall (11H + Jupiter)
- event_tax_refund (6H exit + Mercury)
- event_property_loss (4H + 12H)
- event_land_acquisition (4H + 11H)
- event_plot_sale (2H + 4H + 11H)
- event_mortgage_finalize (6H Mercury)
- event_ancestral_inheritance (4H + 8H Jupiter)
- event_fortune_loss (9H + 12H)

### Phase 4 (Next 30 — Relationships/Family)
- event_friend_acquisition (11H + Venus/Jupiter)
- event_betrayal_friend (11H + 12L + Ketu)
- event_elder_sibling_birth (11H)
- event_elder_sibling_marriage (11H + Venus)
- event_elder_sibling_death (11H + 8L)
- event_father_in_law_event (7H + 2H + 9H)
- event_mother_in_law_event (7H + 4H + 4H)
- event_uncle_maternal (4H + 3H)
- event_uncle_paternal (3H + 9H)
- event_aunt_event (3H + 11H)
- event_cousin_event (3H + 11H)
- event_step_family_event (2H + Rahu)
- event_adoption (5H + Rahu/Jupiter)
- event_engagement_break (7H + Saturn)
- event_divorce (7H + 12L)
- event_widowhood_remarriage (7H second activation)
- event_extramarital_affair (5H + 7H + Rahu)
- event_child_marriage_self (5H)
- event_grandchild_marriage (9H + 5H)
- event_great_grandparent_death (Jupiter MD + 9L 9L = 5H)
- event_pet_death (6H + 8H)
- event_loved_one_death (8H + Maraka)
- event_distant_relative_death (3H + 8H)
- event_neighbor_dispute (3H + 6H)
- event_business_partner_betrayal (7H + 12H)
- event_business_partner_death (7H + 8L)
- event_co_worker_event (6H)
- event_servant_event (6H + Saturn)
- event_landlord_dispute (4H + 6H)
- event_tenant_event (4H + 6H + 11H)

### Phase 5 (Next 30 — Career deep dive)
- event_first_job (10L AD activation)
- event_job_change (10L MD shift + Mercury)
- event_profession_switch (10L + 9L combination)
- event_industry_change (10L different dispositor)
- event_promotion_executive (10L + 11L + Sun strong)
- event_promotion_to_board (10L + 11L + Jupiter)
- event_founder_role (10L + 5L)
- event_ceo_role (10L + Sun + Saturn)
- event_advisor_role (10L + 9L)
- event_consultant_phase (10L + Mercury)
- event_corporate_scandal (10H + 12H + Rahu)
- event_fame_peak (1H + 10H + Moon)
- event_fame_loss_scandal (10H + 12H + Ketu)
- event_government_position (10H + Sun + Saturn)
- event_diplomatic_role (7H + 9H)
- event_military_role (3H + 6H + Mars)
- event_judicial_role (9H + Jupiter)
- event_teaching_role (2H + 5H + Jupiter)
- event_research_role (8H + Mercury + Saturn)
- event_writing_career_milestone (3H + Mercury + Jupiter)
- event_acting_career_milestone (5H + Venus + Rahu)
- event_singing_career_milestone (2H + Venus)
- event_dancing_career_milestone (Venus + Moon)
- event_sports_career_milestone (3H + Mars)
- event_engineering_career_milestone (Mercury + Saturn + Mars)
- event_medical_career_milestone (8H + Saturn + Sun)
- event_law_career_milestone (9H + Jupiter)
- event_finance_career_milestone (2H + 11H + Mercury)
- event_tech_career_milestone (Mercury + Rahu + 11H)
- event_civil_service_milestone (10H + Sun + Saturn)

### Phase 6 (Next 30 — Spiritual/Religious/Karmic)
- event_pilgrimage (9L + 12L + Ketu)
- event_guru_initiation (5H + Jupiter + Ketu)
- event_religious_conversion (Jupiter MD shift / Rahu)
- event_meditation_breakthrough (12H + Ketu + Moon)
- event_kundalini_awakening (Saturn + Ketu)
- event_psychic_experience (Ketu + Rahu + Moon)
- event_past_life_recall (Ketu + 12H)
- event_dream_significant (Moon + Ketu + 12H)
- event_temple_visit_major (9H Jupiter)
- event_chant_completion (5H + Jupiter)
- event_mantra_initiation (5H + Jupiter)
- event_yagna_performance (9H + Jupiter)
- event_diksha_received (5H + Jupiter + Ketu)
- event_renunciation (12H + Ketu)
- event_monastic_phase (12H + Ketu + Saturn)
- event_oracle_dream (Moon + Mercury + Ketu)
- event_synchronicity_peak (Ketu strong)
- event_divine_intervention (9H + Jupiter favorable)
- event_curse_lifted (6H exit + Jupiter)
- event_blessing_received (9H + 11H + Jupiter)
- event_atonement_phase (12H + Saturn + Jupiter)
- event_karma_purification (Saturn + Ketu + 12H)
- event_moksha_pursuit (12H + Ketu)
- event_book_of_dharma (9H + Jupiter)
- event_prophetic_vision (Moon-Ketu / Ketu MD)
- event_astral_travel (12H + Ketu)
- event_divine_call (9H + Jupiter + Ketu)
- event_religious_persecution (6H + 12H + Sat)
- event_oracle_consult (9H + Jupiter + Ketu)
- event_temple_donation (12H + Jupiter)

### Phase 7-10: Specialized Categories
- Phase 7: **Cross-tradition events** — Saham activations (Tajik), KP Sub-lord events, Lal Kitab specific yogas, Nadi-specific predictions
- Phase 8: **Divisional chart events** — D2/D3/D4/D7/D12/D16/D20/D24/D27/D30/D40/D45/D60 sub-dashas per divisional
- Phase 9: **Yoga maturation events** — Special yogas (Mahapadma, Pakshobhani, Sakata, Daridra, Guru Chandala, Vish, Matri Dosha, Putra Dosha activations)
- Phase 10: **Western/Chinese/Numerology specific** — Progressed Sun, Pluto transits, BaZi luck pillars, Personal Year transitions, Pinnacle changes, Karmic numbers

---

## 📝 Function Template (FOLLOW EXACTLY)

Every new event_* function MUST follow this pattern:

```python
def event_<name>(chart, ds, tr, yogas, age):
    """Short description — what life event this captures.
    Optional: which celebrity test it catches.
    """
    # 1. AGE GUARD — Always required
    if age < <min> or age > <max>: return None

    # 2. Setup
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h<N>_lord = _lord(lagna_idx, <N>)  # relevant house lord(s)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    score = 0; why = []

    # 3. PRIMARY rule (highest weight — house lord activation)
    if md == h<N>_lord:
        score += 3; why.append(f"<N>L ({h<N>_lord}) MD — <house> active")
    elif ad == h<N>_lord:
        score += 2; why.append(f"<N>L AD")

    # 4. KARAKA rule (planet karaka of this life domain)
    if md == "<karaka>" or ad == "<karaka>":
        score += 2; why.append("<karaka> active")

    # 5. SECONDARY combinations
    if md == "X" and ad == "Y":
        score += 2; why.append("X+Y combo")

    # 6. NATAL chart booster
    if _h(pos, "<planet>") in [<houses>]:
        score += 1; why.append("natal placement bonus")

    # 7. TRANSIT booster (if relevant)
    transit_match = next((t for t in tr if t.get("transit")=="<P>"
                          and t.get("natal")=="<Q>"
                          and t.get("severity") in ("MEDIUM","HIGH","VERY HIGH")), None)
    if transit_match:
        score += 1; why.append(f"transit {transit_match.get('label')}")

    # 8. THRESHOLD GATE — most functions use < 4 or < 5
    if score < <threshold>: return None

    # 9. RETURN dict with EXACT keys
    return {
        "event": "<one-line description of what happened>",
        "category": "<short_snake_case_category>",
        "severity": min(5, score // 2 + 1),
        "yoga": None,  # or yoga name if relevant
        "why": why,
        "source": "<X>L + <Y> + <karaka> (Classical Source Ch.N)",
    }
```

**Required fields in return dict:**
- `event` — string, one-line event description
- `category` — short snake_case (e.g. "vehicle", "tax_dispute", "saturn_return")
- `severity` — int 1-5
- `yoga` — None or yoga name string
- `why` — list of strings explaining which rules fired
- `source` — string citing classical text (BPHS Ch.N, Phaladeepika Ch.N, etc.)

---

## 🧪 Validation Protocol (CRITICAL — Run AFTER every batch)

**After adding a batch of new functions:**

```bash
cd F:/astro/runtime
python _accuracy_scorer.py 2>&1 | tail -22
```

**MUST CONFIRM:**
- Overall accuracy ≥ 80.3% (current baseline)
- No celebrity score drops by more than 5pp
- All 16 celebrities still appear in output

**If any regression:**
1. Identify which function caused it (binary search: comment out half, test, comment out half of those, etc.)
2. Lower the offending function's threshold OR narrow its dasha conditions
3. NEVER widen aliases in `_accuracy_scorer.py` to mask the regression — that defeats the test

**Then run reverse audit:**
```bash
python _reverse_audit.py 2>&1 | grep -E "VERDICT|rules fired"
```

**MUST CONFIRM:** 8/8 events still show correct verdicts (6 fired + 2 silent).

---

## 🔄 Sync Protocol (After every batch is validated)

```bash
# Sync engine to VPS
scp -P 22 F:/astro/runtime/event_predictor_v2.py root@46.28.44.225:/opt/astro/runtime/

# Verify VPS imports cleanly
ssh root@46.28.44.225 "cd /opt/astro && source venv/bin/activate && cd runtime && python3 -c 'from event_predictor_v2 import ALL_PATTERNS_V2; print(len(ALL_PATTERNS_V2))'"

# Run VPS accuracy
ssh root@46.28.44.225 "cd /opt/astro && source venv/bin/activate && cd runtime && python3 _accuracy_scorer.py 2>&1 | grep OVERALL"

# md5 confirm match
ssh root@46.28.44.225 "md5sum /opt/astro/runtime/event_predictor_v2.py"
cd F:/astro && md5sum runtime/event_predictor_v2.py
```

**Both md5s MUST match.**

---

## 📋 Update Category Aliases (if needed)

When adding functions that emit NEW categories, also update `F:/astro/runtime/_accuracy_scorer.py`:

Search for `CAT_ALIASES` and add mapping for any new category:

```python
CAT_ALIASES = {
    "career": {"career", "career_breakthrough", "education", "promotion", "business"},  # add new
    "wealth": {"wealth", "wealth_peak", "property", "vehicle", "inheritance"},  # add new
    # etc.
}
```

This is OPTIONAL — only needed if accuracy_scorer should treat the new category as matching an existing known-event category.

---

## 🗂 File Inventory (current state)

| File | Purpose | Lines |
|---|---|---|
| `runtime/event_predictor_v2.py` | Main predictor with 47 event functions | ~1,710 |
| `runtime/_accuracy_scorer.py` | Validates 16-celeb baseline | ~280 |
| `runtime/_reverse_audit.py` | Classical rule attribution check | ~340 |
| `runtime/_battle_vijay.py` | OLD vs NEW engine comparison | ~190 |
| `runtime/_extract_all_rules.py` | Generates ALL_RULES.pdf from code | ~480 |
| `runtime/_full_categories_pdf.py` | Generates CATEGORY_LIST.pdf | ~400 |
| `charts/*.json` | 23 chart JSONs (16 celebs + 6 personal + Vijay) | — |
| `ATRO_ALL_RULES.pdf` | Auto-generated rule reference | 46 KB |
| `ATRO_FULL_CATEGORY_LIST.pdf` | Master category inventory | 39 KB |
| `ANTIGRAVITY_HANDOFF.md` | THIS document | — |

---

## ⚠️ Common Pitfalls to Avoid

1. **DON'T import new modules just for one function** — keep dependencies in event_predictor_v2.py minimal. Use only `_lord`, `_h`, `_dig` from the existing helper set.

2. **DON'T forget age guards** — every function needs `if age < X or age > Y: return None` at the top. Without this, the function fires for newborns/infants too.

3. **DON'T set threshold too low** — < 3 causes false positives in 5-10% of charts. < 4 is safe. < 5 is conservative.

4. **DON'T duplicate category names** — `_accuracy_scorer.py` aliases assume one category per concept. If you have `event_vehicle_purchase` and `event_vehicle_loss`, use categories "vehicle" and "vehicle_loss" not both "vehicle".

5. **DON'T add functions that emit NEUTRAL events** (every chart has them) — that's noise. Only add functions that fire SELECTIVELY based on specific dasha/transit conditions.

6. **DON'T modify the original 17 functions** without re-running `_reverse_audit.py` — those rules are validated against classical BPHS/Phaladeepika citations.

7. **ALWAYS append new functions BEFORE the final `ALL_PATTERNS_V2 = [...]` block**, not after.

8. **ALWAYS cite a classical source** in the `source` field. If you can't cite, the rule isn't ready.

---

## 🎯 Target Milestones

| Phase | Functions | Total | Coverage |
|---|---|---|---|
| Phase 0 (May 22) | 17 | 17 | ~4% |
| **Phase 1 (May 26 — DONE)** | **30** | **47** | **~12%** |
| Phase 2 | 30 | 77 | ~19% |
| Phase 3 | 30 | 107 | ~27% |
| Phase 4 | 30 | 137 | ~34% |
| Phase 5 | 30 | 167 | ~42% |
| Phase 6 | 30 | 197 | ~49% |
| Phase 7 | 30 | 227 | ~57% |
| Phase 8 | 30 | 257 | ~64% |
| Phase 9 | 30 | 287 | ~72% |
| **Phase 10 (COMPLETE)** | **~110** | **~398** | **~100%** |

**Estimated effort per phase: 5-8 hours** (30 functions × 10-15 min each + validation).

**Total remaining: ~50-80 hours of focused work.**

---

## 🧠 Decision Rules When Adding New Categories

1. **Is there a classical source for this prediction?**
   - YES → write the function
   - NO → skip (no rule fidelity)

2. **Does it have a clear dasha/transit signature?**
   - YES → encode it
   - NO → it's continuous (personality/health) not event-based — different system

3. **Does the category overlap with an existing one?**
   - SIGNIFICANTLY → extend existing function instead of creating new
   - PARTIALLY → new function with category mapping in alias

4. **Will it fire for >5% of charts?**
   - YES → fine
   - NO → it's too narrow, generalize the rule OR skip

5. **Has the threshold been tested on 16-celeb baseline?**
   - YES → ship it
   - NO → not ready

---

## 📞 Cross-References

When in doubt about an event-type:
- **BPHS** (Brihat Parashara Hora Shastra): Ch.13 (Marriage), 23 (Property), 25 (Career), 32 (Father), 40 (Disease), 45-46 (Death/Maraka), 80 (Marriage via D9)
- **Phaladeepika** by Mantreswara: Ch.6 (Houses), 7 (Career), 10 (Property), 13 (Karakas), 27 (Eclipses)
- **Saravali** by Kalyanavarma: Ch.30 (Wealth), 39 (Jupiter/Wisdom), 40 (Yogas)
- **Hora Sara**: Ch.25 (Spirituality/Foreign Travel)
- **Books library** at `F:/astro/Books/` (1.9 GB) — search by topic

---

## ✅ Continuation Checklist for Antigravity

When picking up Phase 2:

- [ ] Read this handoff document fully
- [ ] Read `F:/astro/ATRO_FULL_CATEGORY_LIST.md` for the remaining ❌ Missing categories
- [ ] Pick a batch of 5-10 related functions from Phase 2 list above
- [ ] Write each function following the template
- [ ] Append to `event_predictor_v2.py` BEFORE the `ALL_PATTERNS_V2 = [...]` block
- [ ] Add each function name to `ALL_PATTERNS_V2` list
- [ ] Run `python _accuracy_scorer.py` — confirm ≥ 80.3%
- [ ] Run `python _reverse_audit.py` — confirm 8/8 verdicts unchanged
- [ ] If both pass: sync to VPS (`scp` then verify md5)
- [ ] If either fails: debug + lower threshold OR narrow conditions
- [ ] Update CLAUDE.md changelog with phase completion
- [ ] Move on to next batch

---

## 🎁 Final Note

Each new function is a small, testable, classical-text-cited rule.
The framework rewards patience — better to add 10 well-validated rules than 50 noisy ones.

The OLD engine (`event_predictor_v2.py`) is now:
- **47 functions** across **~30 categories**
- **80.3% accuracy** on 16-celeb / 127-event baseline
- **86% accuracy** on Vijay 28-event battle
- **100% classical-rule fidelity** (8/8 reverse audit)

Continue with the SAME discipline and the engine will hit ~95% coverage with another 200+ functions.

**Good luck. Build well.**
