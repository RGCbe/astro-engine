# Corpus Completion Runbook - Incomplete `_deep` Extractions

**Date:** 2026-06-02  
**Status:** **Partial** � 3/5 target books complete (BPHS1, Sarvartha_Chintamani, KP_Reader_3_Predictive). Bhrigu + Jataka retry running on VPS. Corpus **15,613 ? 18,174** unique rules.  
**Live progress:** [EXTRACTION_STATUS.md](./EXTRACTION_STATUS.md)

Use this runbook to resume the 5 remaining incomplete `gemma_extractions/*_deep.json` files.

---

## 1. Incomplete inventory (2026-06-02)

| File | Progress | Missing | Raw rules | In live corpus? | Source text VPS |
|---|---:|---:|---:|---|---|
| `Jataka_Bharanam_deep.json` | 59 / 505 | **88.3%** | 202 | **Yes** | `/opt/astro/Books/Jataka_Bharanam_extracted.txt` |
| `Bhrigu_Samhita_deep.json` | 122 / 219 | **44.3%** | 2,112 | **Yes** | `/opt/astro/Books/Bhrigu_Samhita_extracted.txt` |
| `KP_Reader_3_Predictive_deep.json` | 210 / 378 | **44.4%** | 2,560 | **Yes** | `/opt/astro/Books/KP_Reader_3_Predictive_extracted.txt` |
| `Sarvartha_Chintamani_deep.json` | 108 / 130 | **16.9%** | 2,396 | **Yes** | `/opt/astro/Books/Sarvartha_Chintamani_extracted.txt` |
| `BPHS1_deep.json` | **203 / 203** | **done** | **3,100** | **Yes** | `/opt/astro/Books/BPHS1_extracted.txt` |
| `Surya_Siddhanta_deep.json` | 219 / 320 | **31.6%** | 1,271 | **No** (excluded) | `/opt/astro/Books/Surya_Siddhanta_extracted.txt` |

**Corpus count:** 15,581 unique (before BPHS1 proof) -> **15,613** (after). Raw rules 17,066 -> 17,100.

Audit helper:

```bash
cd /opt/astro   # or F:/astro locally
python scratch/_inventory_incomplete.py
python scratch/_analyze_chunk_coverage.py
python scratch/_estimate_remaining_source.py
python /tmp/_corpus_stats_once.py   # full path on VPS after scp from scratch/
```

---

## 2. Tooling and keys

### A. Extraction script (restored)

| File | Purpose |
|---|---|
| `_workbench/_deep_extract.py` | Resume CLI + `_smart_chunks`, `_guess_verse_ids` |
| `_workbench/.gitignore` | Ignores `.keys/` if legacy export used |

CLI:

```bash
python _workbench/_deep_extract.py --book BPHS1 --resume --vault-direct
python _workbench/_deep_extract.py --book Sarvartha_Chintamani --resume --vault-direct
python _workbench/_deep_extract.py --book BPHS1 --resume --vault-direct --max-chunks 1  # smoke test
```

Flags:

- `--resume` (required) - continue from `last_chunk_processed + 1`
- `--vault-direct` - unlock `/root/api-expense-manager` vault in-process (VPS only; reads `.env`, never prints keys)
- `--max-chunks N` - limit chunks per run
- `--target-chars N` - override chunk size (auto-calibrates to `n_chunks_total` by default)

Provider failover order: **google, cerebras, groq, nvidia, sambanova** (vault checkout per provider).

**Local Windows:** vault HTTP at `127.0.0.1:5055` is not reachable; do not export keys to disk. Run extractions on VPS only.

### B. API keys - api-vault on VPS

| Location | Status |
|---|---|
| Real DB | `/root/api-expense-manager/data/expense_manager.db` (~3.5 MB) |
| Stub (ignore) | `vault.db` (0 bytes) |
| PM2 `api-vault` | online, port **5055** |
| Checkout | in-process via `--vault-direct` OR HTTP with `VAULT_TOKEN` |

List providers (masked, no secrets):

```bash
ssh root@46.28.44.225
scp F:/astro/scratch/_vault_list_keys.py root@46.28.44.225:/tmp/
python3 /tmp/_vault_list_keys.py
```

Live quota per provider (OK / near_limit / exhausted; last4 only, no keys):

```bash
ssh root@46.28.44.225
scp F:/astro/scratch/_vault_quota_summary.py root@46.28.44.225:/tmp/
# loads VAULT_MASTER_PASSWORD from /root/api-expense-manager/.env
python3 /tmp/_vault_quota_summary.py
```

Or vault UI / HTTP (session auth): `GET http://127.0.0.1:5055/api/keys/quotas`

Fix cerebras model 404 in vault DB only (probes API, updates `api_keys.model`):

```bash
python3 /tmp/_fix_cerebras_model.py   # after scp from scratch/_fix_cerebras_model.py
```

Automated quota check + resume queue (Sarvartha ? KP ? Bhrigu ? Jataka):

```bash
scp F:/astro/scratch/_vps_corpus_quota_resume.sh root@46.28.44.225:/opt/astro/scratch/
nohup bash /opt/astro/scratch/_vps_corpus_quota_resume.sh &
tail -f /opt/astro/logs/corpus_quota_resume_*.log
```

`_deep_extract.py --vault-direct` skips providers classified **exhausted** or **error_model** before each chunk.

Active LLM providers (last4 only): `cerebras` (...ee3), `groq` (...kY9), `google` (...5Kg), `nvidia` (...ib7), `sambanova` (...436).

Optional HTTP checkout (register **astro** service in vault UI first):

```bash
export VAULT_URL=http://127.0.0.1:5055
export VAULT_TOKEN=<service bearer from vault dashboard>
export VAULT_SERVICE=astro
python _workbench/_deep_extract.py --book Sarvartha_Chintamani --resume
```

Legacy flat export (avoid for corpus; use only if vault API down):

```bash
# See scratch/_vault_export_to_keys.py - writes _workbench/.keys/*.key (gitignored)
```

### C. Do NOT merge `_gemma` into `_deep`

`engine/corpus.py` excludes `*_gemma.json` when a `*_deep.json` exists. Only resume `_deep_extract.py`.

---

## 3. Resume procedure (VPS)

### Step 1 - Deploy script

```bash
scp -r F:/astro/_workbench root@46.28.44.225:/opt/astro/
ssh root@46.28.44.225 "python3 -c \"import sys; sys.path.insert(0,'/opt/astro'); from _workbench._deep_extract import _smart_chunks; print('OK')\""
```

### Step 2 - Baseline corpus stats

```bash
ssh root@46.28.44.225
scp F:/astro/scratch/_corpus_stats_once.py root@46.28.44.225:/tmp/
python3 /tmp/_corpus_stats_once.py
```

### Step 3 - Resume extractions (priority order)

```bash
ssh root@46.28.44.225
cd /opt/astro

# Done 2026-06-02:
python3 _workbench/_deep_extract.py --book BPHS1 --resume --vault-direct

# Next (21 chunks):
python3 _workbench/_deep_extract.py --book Sarvartha_Chintamani --resume --vault-direct

# Larger gaps:
python3 _workbench/_deep_extract.py --book Jataka_Bharanam --resume --vault-direct
python3 _workbench/_deep_extract.py --book Bhrigu_Samhita --resume --vault-direct
python3 _workbench/_deep_extract.py --book KP_Reader_3_Predictive --resume --vault-direct

# Optional (excluded from live corpus):
python3 _workbench/_deep_extract.py --book Surya_Siddhanta --resume --vault-direct
```

### Step 4 - Validate

```bash
python3 scratch/_inventory_incomplete.py
python3 /tmp/_corpus_stats_once.py
```

Expect `is_complete: true` when `last_chunk_processed >= n_chunks_total - 1`.

### Step 5 - Restart engine (corpus cached at startup)

Extractions run in-place under `/opt/astro/gemma_extractions/`. After each book:

```bash
pm2 restart astro-engine
sleep 4
pm2 logs astro-engine --lines 10 --nostream
```

Sync JSON to local (optional):

```bash
scp root@46.28.44.225:/opt/astro/gemma_extractions/BPHS1_deep.json F:/astro/gemma_extractions/
```

---

## 4. BPHS1 proof (2026-06-02)

| Metric | Before | After |
|---|---:|---:|
| BPHS1 `last_chunk_processed` | 199 | **202** |
| BPHS1 raw rules | 3,061 | **3,100** (+39) |
| BPHS1 `is_complete` | false | **true** |
| Corpus unique rules | 15,581 | **15,613** (+32 after dedup) |

Notes: chunks 200-202 extracted via **groq** (google returned malformed JSON; cerebras model 404 in vault). ~2.5 min total.

---

## 5. Remaining effort estimate

| Book | Unprocessed chunks | ~Chars remaining |
|---|---:|---:|
| Jataka_Bharanam | 445 | 407 KB |
| Bhrigu_Samhita | 96 | 353 KB |
| KP_Reader_3_Predictive | 167 | 445 KB |
| Sarvartha_Chintamani | 21 | 71 KB |
| Surya_Siddhanta | 100 | astronomy (excluded) |

Plan multi-hour runs; use `--max-chunks` to batch across sessions.

---

## 6. Checklist

- [x] Reconstruct `_workbench/_deep_extract.py`
- [x] Vault integration without exposing keys (`--vault-direct` on VPS)
- [x] BPHS1 proof + `pm2 restart astro-engine`
- [x] Sarvartha_Chintamani resume (2026-06-02, `is_complete: true`)
- [ ] Jataka_Bharanam / Bhrigu_Samhita / KP_Reader_3 resume
- [ ] Confirm all `is_complete: true` + corpus count stable

---

## 7. Related files

| File | Purpose |
|---|---|
| `_workbench/_deep_extract.py` | Main resume extractor |
| `engine/tests/test_deep_extract.py` | `_smart_chunks`, `_guess_verse_ids` tests |
| `scratch/_vault_list_keys.py` | List vault providers (masked) |
| `scratch/_vault_export_to_keys.py` | Legacy flat export (avoid) |
| `scratch/_corpus_stats_once.py` | BPHS1 + corpus describe one-liner |
| `F:/api-expense-manager/vault_client.py` | HTTP checkout reference |
