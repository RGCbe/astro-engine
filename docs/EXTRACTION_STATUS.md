# Deep extraction status

**Updated:** 2026-06-03 (local + VPS `46.28.44.225`)


## RUNNING (resumed 2026-06-03)

**Status:** **ALL TARGET BOOKS COMPLETE** (2026-06-04). Bhrigu 219/219, Jataka 373/373, KP, Sarvartha, BPHS1 done. Corpus ~19.4k rules. `astro-engine` restarted.

**Next (P0):** `chart_profile` + `multi_source_synthesis` wired in `engine_orchestrator.py` (lagna-filtered topic confidence).

**Pause again:**
```bash
ssh root@46.28.44.225
echo 'paused' > /opt/astro/scratch/EXTRACTION_PAUSED.flag
pkill -f '_vps_corpus_retry|_deep_extract'
```

**Completed this session:**

| Book | Chunks | Status |
|------|--------|--------|
| BPHS1 | 203/203 | **done** |
| Sarvartha_Chintamani | 130/130 | **done** |
| KP_Reader_3_Predictive | 378/378 | **done** (finished retry pass 1 ~12:xx UTC) |

**Still incomplete:**

| Book | Chunks | Missing | Notes |
|------|--------|---------|--------|
| Bhrigu_Samhita | 126/219 | 42.5% | paused at chunk 126 |
| Jataka_Bharanam | 180/505 | 64.4% | paused |
| Surya_Siddhanta | 220/320 | excluded | not in live corpus |

**Corpus (VPS live at pause):** **18,189** unique rules (19,957 raw, 1,768 dup merges, 41 books). Baseline was **15,613** (+2,576).

## Summary

| Book | % complete | Last activity (VPS) | Status |
|------|------------|---------------------|--------|
| BPHS1 | **100%** (203/203) | 2026-06-02 | **done** |
| Sarvartha_Chintamani | **100%** (130/130) | 2026-06-02 10:30 UTC | **done** |
| KP_Reader_3_Predictive | **100%** (378/378) | 2026-06-02 ~12:00 UTC | **done** |
| Bhrigu_Samhita | **57.5%** (126/219) | 2026-06-02 (paused) | **paused** |
| Jataka_Bharanam | **35.6%** (180/505) | 2026-06-02 12:32 UTC | **paused** |
| Surya_Siddhanta | 68.8% (220/320) | 2026-04-27 (local) | **excluded** |

**Orchestration:** pass 1 log `/opt/astro/logs/corpus_retry.log`; pass 2 `/opt/astro/logs/corpus_retry2.log`.

**PM2:** `api-vault` online (10d), `astro-engine` online (~62m uptime at check).

## API / errors

| Provider | State |
|----------|--------|
| google | **exhausted** (skipped) |
| sambanova | **exhausted** (skipped) |
| cerebras | **near_limit** (primary; gpt-oss-120b) |
| groq | OK |
| nvidia | OK |

Log noise: vault lease expiry, per-key rate-limit cooldowns (60-120s). Extraction continues on **cerebras -> groq -> nvidia** failover.

## Local vs VPS

Local `F:\astro\gemma_extractions\*_deep.json` is **stale** except **BPHS1** (synced 2026-06-02). Authoritative progress: VPS `/opt/astro/gemma_extractions/`. Run `scratch/_book_progress.py` on VPS (or scp to `/tmp`) for chunk counts.

## What is left (ETA rough)

1. **Jataka_Bharanam** - ~345 chunks; at ~2-60s/chunk with cerebras, **many hours** (rate limits add jitter).
2. **KP_Reader_3_Predictive** - ~48 chunks after resume script re-run or manual `--book KP_Reader_3_Predictive --resume`.
3. **Bhrigu_Samhita** - ~94 chunks; same.
4. Re-sync finished `_deep.json` to `F:\astro` and re-run audit helpers from `CORPUS_COMPLETION_RUNBOOK.md`.

## References

- `docs/CORPUS_COMPLETION_RUNBOOK.md`
- `docs/CORPUS_QUALITY_AUDIT.md`

