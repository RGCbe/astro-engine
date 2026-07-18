# Parallel-Work Coordination Protocol

**Effective:** 2026-05-26
**Participants:** Claude (OLD engine — rule-based) + Antigravity (NEW engine — optimized GAC)
**Purpose:** Avoid conflicts while both AIs improve Atro simultaneously.

---

## 🛡 FILE OWNERSHIP ZONES

### 🤖 CLAUDE TERRITORY (do not edit from Antigravity)

| File | Role |
|---|---|
| `runtime/event_predictor_v2.py` | Rule-based event functions (`event_*`) |
| `runtime/divisional_dasha.py` | D9/D10 Vimshottari computation |
| `runtime/granular_dasha.py` | Vimshottari full timeline |
| `runtime/comprehensive_yogas.py` | Classical yoga detectors |
| `runtime/sade_sati.py` | Saturn cycles |
| `runtime/transit_engine.py` | Transit detection |
| `runtime/kp_paddhati.py` | KP sub-lord |
| `runtime/_accuracy_scorer.py` | OLD engine validation |
| `runtime/_reverse_audit.py` | Classical rule attribution |
| `runtime/_extract_all_rules.py` | OLD engine rule extraction |
| `runtime/_full_categories_pdf.py` | Category list PDF generator |
| `ANTIGRAVITY_HANDOFF.md` | Roadmap to Phase 10 |
| `ATRO_FULL_CATEGORY_LIST.md` + `.pdf` | Master category inventory |
| `ATRO_ALL_RULES.pdf` | OLD engine rule reference |
| `ATRO_VS_ASTROSAGE.md` | AstroSage comparison |
| `REVERSE_AUDIT_REPORT.md` | Reverse-direction audit doc |
| `reports/jun 2026/2026-06-02/report/accuracy/ACCURACY_REPORT.json` | Latest accuracy run output |
| `~/.claude/CLAUDE.md` | Global Claude config + changelog |
| `~/.claude/projects/` (astro workspace memory) | Claude memory files |

### 🚀 ANTIGRAVITY TERRITORY (do not edit from Claude)

| File | Role |
|---|---|
| `scratch/optimize_multi_actor.py` | 9-actor optimizer |
| `scratch/optimize_*.py` | All hyperparameter optimizers |
| `scratch/vijay_*.py` | Vijay-specific scripts |
| `scratch/astro_numerology_weights.json` | Vijay-optimized weights |
| `scratch/weights_*.json` | Per-actor weight files |
| `scratch/vijay_lifeline.md` | Vijay forensic mapping |
| `scratch/diff_report.md` | Antigravity diff outputs |
| `scratch/local_scan.json` + `vps_scan.json` | Sync inventories |
| `scratch/_*` | Antigravity working files |
| `engine/chinese_engine.py` | BaZi + Zi Wei Dou Shu |
| `engine/mayan_engine.py` | Tzolk'in calendar |
| `engine/numerology_engine.py` | Chaldean + Pythagorean |
| `engine/nadi_jyotish.py` | Bhrigu Nandi Nadi |
| `engine/western_engine.py` | Tropical + Hellenistic |
| `engine/tajik.py` | Varshaphala annual |
| `engine/yogas_extended.py` | Extended yoga catalog |
| `engine/jaimini_full.py` | Full Jaimini wrapper |
| `engine/reading.py` + `engine/evaluator.py` | Reading framework |
| `engine/corpus.py` | Corpus search |

### 🤝 SHARED FILES (coordinated edits required)

| File | Shared because |
|---|---|
| `runtime/_battle_vijay.py` | OLD + NEW both compared here |
| `charts/*.json` | Both AIs may add celebrity charts |
| `engine/book_rules.py` | Both query the 970-rule index |
| Any new chart JSONs | Coordinate to avoid duplicates |
| VPS `/opt/astro/` | Both sync here |
| `current_state.md`-style trackers | Both write status |

---

## 📜 SHARED FILE MODIFICATION RULES

### `_battle_vijay.py`
- **OLD engine section** (`run_old_engine` function): Claude territory
- **NEW engine section** (`run_new_engine` function): Antigravity territory
- **Main / scoring / output**: shared — only edit if both agree
- **Add new engine variant?** → New function, register in main, don't replace existing

### `charts/*.json`
- Before adding a new chart, **check if it already exists**
- If both AIs add the SAME celebrity, the LAST writer wins (md5 mismatch will be visible in sync logs)
- **Convention:** if you're adding a chart, prefix with your originator: e.g. `_anti_kamal_haasan_chart.json` until verified, then rename to canonical `kamal_haasan_chart.json`
- **Existing charts** (Sachin, Modi, Dhoni, Rahman, Rekha, Amitabh, Aishwarya, Indira, Mahatma, Steve Jobs, Hawking, Lata, Mukesh, Virat, SRK, Ganguly, Aamir, Salman, Hrithik, Rajinikanth, Kamal, Vijay, Manoj, Sree, Krishnan, Jayaprakesh, Sivadhanya, Karnan) — DO NOT overwrite unless coordinating

### `engine/book_rules.py`
- READ ONLY for both. If a fix is needed, agree first.

---

## 🔒 LOCK MECHANISM (lightweight)

Before editing a SHARED file, write a touch-file:

```bash
# Claude before editing _battle_vijay.py:
touch F:/astro/.lock_battle_vijay_claude

# Antigravity before editing same:
touch F:/astro/.lock_battle_vijay_antigravity
```

**Rule:** If you see another AI's lock file present, **wait or pick a different file**. Lock files older than 1 hour can be considered stale and deleted.

After editing + syncing:
```bash
rm F:/astro/.lock_battle_vijay_claude
```

---

## 🔄 SYNC SCHEDULE

### Per-batch sync (both AIs follow)

After EVERY batch of edits:
1. Test locally (must hold baselines)
2. Sync to VPS (`scp -P 22 <file> root@46.28.44.225:/opt/astro/...`)
3. Verify md5 match (local vs VPS)
4. Append to `SYNC_LOG.md` with timestamp + who + what

### Daily sync window
- Both AIs do a full inventory diff at ~22:00 UTC
- Compare local vs VPS, flag any drift
- Use `scratch/local_scan.json` + `vps_scan.json` if Antigravity maintains them
- Or use Claude's md5 batch check

### Engine modification rule
- **Claude never edits NEW engine code** (`scratch/`, `engine/chinese|mayan|numerology|nadi|western|tajik|yogas_extended|jaimini_full|reading|evaluator|corpus`)
- **Antigravity never edits OLD engine code** (`event_predictor_v2.py`, `divisional_dasha.py`, `comprehensive_yogas.py`, `transit_engine.py`, etc.)
- Each can READ the other's code freely

---

## ⚖️ CONFLICT RESOLUTION

### If both edit the same file:
1. **VPS state is authoritative** (last good sync)
2. Newer local edit is REJECTED if it overwrites the other AI's changes
3. The displaced AI re-applies their change to current state, syncs again
4. Both AIs maintain a log entry in `SYNC_LOG.md`

### If both add the same category/function:
1. Compare implementations — if both classical-rule-based, keep Claude's (rule-fidelity)
2. If one is hyperparameter-fit (NEW engine territory), keep that one in NEW engine
3. NEVER duplicate function names across files

### If one breaks the other:
- **Baseline tests must still pass for both engines after any change**
- OLD: `_accuracy_scorer.py` ≥ 80.3% / `_reverse_audit.py` 8/8 verdicts
- NEW: `optimize_multi_actor.py` 9/9 actors at 100% / Vijay 28/28 holding
- If you break the other engine's baseline, REVERT your last change

---

## 📊 STATUS DASHBOARD

Both AIs append to `STATUS.md` in `F:/astro/` (synced VPS) with:

```
[2026-05-26 17:30] CLAUDE — Phase 1 complete. event_* functions 17→47. Accuracy 80.3%.
[2026-05-26 17:45] ANTIGRAVITY — Vijay battle NEW engine 100% via enhanced GAC + double-Rahu.
[2026-05-26 18:00] CLAUDE — Phase 2 started: event_birth_circumstances + event_voice_loss.
```

Read STATUS.md before starting work to see if the other AI is in the middle of something.

---

## 🎯 PHASE COORDINATION

### Claude (OLD engine) — Phases 2-10
- Each phase = 30 functions, ~5-8 hrs
- Follow `ANTIGRAVITY_HANDOFF.md` roadmap
- Append-only to `event_predictor_v2.py`

### Antigravity (NEW engine) — Parallel improvements
- Refine GAC hyperparameter scoring per category
- Add D9/D10/Chara dasha layers to optimizer
- Add karaka transit triggers
- Add yoga-context boosts
- Train separate non-movie weights
- Refer to `NEW_ENGINE_IMPROVEMENT_OPPORTUNITIES.md` for the spec

### Mutual baseline tests (after every batch)
Both AIs must run BOTH baselines:
```bash
# OLD engine baseline:
python F:/astro/runtime/_accuracy_scorer.py  # ≥ 80.3%
python F:/astro/runtime/_reverse_audit.py    # 8/8 verdicts

# NEW engine baseline:
python F:/astro/scratch/optimize_multi_actor.py  # 9/9 = 100%
python F:/astro/runtime/_battle_vijay.py         # OLD ≥ 86%, NEW = 100%
```

If your edit makes EITHER engine's baseline drop, revert.

---

## 🚨 RED LINES (never cross)

1. **Do not delete charts in `charts/`** — they're a shared validation asset
2. **Do not modify the original 17 event functions in `event_predictor_v2.py`** — they're classically validated
3. **Do not change `_accuracy_scorer.py` thresholds** (tolerance, year-only buffer, etc.) to mask regressions
4. **Do not modify `ANTIGRAVITY_HANDOFF.md` Phase 1 section** — it's the completed state record
5. **Do not push code that hasn't passed both baselines locally first**
6. **Do not skip md5 verification after sync**

---

## ✅ FAST-PATH FOR ANTIGRAVITY (this session)

Antigravity can immediately:

1. **Improve `run_new_engine()` in `_battle_vijay.py`** (already started — 100% achieved)
2. **Extend `optimize_multi_actor.py`** with NEW celebrities (Sachin, SRK, Aamir, Salman, Hrithik — Bollywood actors)
3. **Build `optimize_general_events.py`** — same framework but for non-movie events (births, deaths, marriages, etc.)
4. **Train `non_movie_weights.json`** alongside the existing film weights
5. **Add D9/D10/Chara dasha** to GAC scoring (per `NEW_ENGINE_IMPROVEMENT_OPPORTUNITIES.md`)
6. **Build comparison dashboard** showing OLD vs NEW per-category on multiple celebrities

Each of these stays in Antigravity territory and doesn't conflict with Claude's Phase 2-10 buildout.

---

## 📞 EMERGENCY CONTACT

If something breaks badly:
- User can revert to last good state via `git` (if initialized) or manual file restore
- VPS has `_archive/` and `_backup/` directories — check there
- `scratch/*.bak.*` timestamped backups exist for NEW engine work
- OLD engine has no .bak yet — but `event_predictor_v2.py` is in git history if needed

---

## 🎁 BENEFITS OF PARALLEL WORK

- 2× iteration speed
- Two completely different methodologies tested in parallel
- Each AI plays to its strength (Claude = code/discipline, Antigravity = optimization/numerology)
- User gets the best of both
- Knowledge sharing via this protocol + status logs

Build well. Coordinate often.
