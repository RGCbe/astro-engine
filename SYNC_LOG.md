# Atro Sync Log

Both AIs log VPS sync events here. Helps detect drift + identify last-good state.

Format: `[TIMESTAMP UTC] AI_NAME — file(s) → VPS — md5 result`

---

[2026-05-26 16:38] CLAUDE — bulk tar: runtime/ + engine/ + charts/ + logic_base/ → /opt/astro/ — 43 MB extracted, 109 runtime + 97 engine + 23 charts

[2026-05-26 16:43] CLAUDE — runtime/event_predictor_v2.py + ANTIGRAVITY_HANDOFF.md → /opt/astro/ — md5 14901e8d76fbae25e395cdf01d44dd4d ✓ match

[2026-05-26 17:00] ANTIGRAVITY — runtime/_battle_vijay.py modified locally (enhanced run_new_engine — Vijay 28/28 = 100%) → /opt/astro/runtime/ — synced

[2026-05-26 17:20] CLAUDE — COORDINATION_PROTOCOL.md + STATUS.md + SYNC_LOG.md written, pushed to VPS

[2026-05-26 17:30] CLAUDE — Final sync: 4 coordination files → /opt/astro/. md5 all match (b191a7c9..., 9ddae73c..., 04dea54e..., 40f99410...). Parallel work mode active.

[2026-05-26 18:30] CLAUDE — event_predictor_v2.py Phase 2+3 (60 functions) → /opt/astro/runtime/. md5 e788658b353f338306270985e9d34d34 ✓ match. ALL_PATTERNS_V2 now 105. Accuracy 80.3% steady.

[2026-05-26 18:45] ANTIGRAVITY — runtime/category_engine.py + runtime/engine_orchestrator.py → /opt/astro/runtime/ — md5 verified, PM2 process 20 hot-reloaded cleanly with 100% remote test success.

[2026-05-26 19:00] CLAUDE — event_predictor_v2.py Phases 4-6 (90 functions) → /opt/astro/runtime/. md5 34bac831d25f2f614f93d4719f2f9948 ✓ match. ALL_PATTERNS_V2 now 190. Accuracy 80.3% steady.

[2026-05-26 19:15] ANTIGRAVITY — runtime/hindi_translations.py → /opt/astro/runtime/ — md5 verified, Hindi Devnagari translation library live on VPS.

[2026-05-26 19:30] CLAUDE — runtime/claude_categories.py (NEW, declarative 80-category catalog) + event_predictor_v2.py (registers Phase 7-10) → /opt/astro/runtime/. md5 2ff94e29e8cfe04e06dd81b9f6306dfe + f281584260acaee6dad37049b636207a ✓. ALL_PATTERNS_V2 = 270 (190 imperative + 80 declarative). Accuracy 80.3% steady.

[2026-05-26 19:45] ANTIGRAVITY — main.py, runtime/tamil_renderer.py, frontend/index.html, static/css/style.css, static/js/app.js → /opt/astro/ — conjoined multi-language report (EN, TA, HI), justified alignment, and AJAX PDF streaming endpoint live in production. Hot-reloaded PM2 astro-engine cleanly.

[2026-05-27 04:22] ANTIGRAVITY — main.py, runtime/generate_report.py, runtime/generate_tamil_pdf.py, runtime/generate_hindi_pdf.py, runtime/tamil_renderer.py, runtime/hindi_translations.py, Outfit fonts, Noto Sans Devanagari fonts → /opt/astro/ — Synced multi-language justified shaping engines, translated generators, and premium font assets to live VPS directories. Restarted PM2 astro-engine cleanly.

[2026-05-27 04:41] ANTIGRAVITY — runtime/category_catalog.py + runtime/category_engine.py + runtime/claude_categories.py + runtime/event_predictor_v2.py → /opt/astro/runtime/ — Synced unified engine balancing files. Remote integration tests passed 100% in 192.9s. PM2 restarted cleanly.

[2026-06-02 06:50] CURSOR — Unified layout: local `F:/astro`, VPS `/opt/astro` (removed nested `full/`). PM2 cwd `/opt/astro`. Old tree archived at `/opt/astro_backup_*`.

[2026-06-02 07:15] CURSOR — Disk cleanup: deleted astro_backup (39G), `_research/repos` (13G), wine-stable, video-decoder, pip/playwright caches. Ephe moved to `/opt/astro/ephe`. Fixed all `/opt/astro/full` paths in code. Disk 86% → 26%.

[2026-06-05 05:15] ANTIGRAVITY — engine/education.py → /opt/astro/engine/ — md5 f18efa46ab654f13527bd9e2bc756103 ✓ match. PM2 process astro-engine reloaded cleanly.

[2026-06-05 10:55] ANTIGRAVITY — reports/jun 2026/manoj/ (English/Tamil PDFs + timeline MDs) → /opt/astro/reports/ — synced successfully.

[2026-06-05 11:20] ANTIGRAVITY — reports/MANOJ_FULL_BOOKLET_EN.pdf + reports/MANOJ_FULL_BOOKLET_TA.pdf (full 23-domain booklets) → /opt/astro/reports/ — synced successfully.
[2026-07-07 07:33] ANTIGRAVITY — Local fix: runtime/compatibility_kuta.py modified to normalize Sanskrit/Tamil rasi names. Not yet synced to VPS.
---



## Sync command reference

```bash
# Single file:
scp -P 22 F:/astro/runtime/<file>.py root@46.28.44.225:/opt/astro/runtime/

# Single file to root:
scp -P 22 F:/astro/<file>.md root@46.28.44.225:/opt/astro/

# Verify md5 match:
ssh root@46.28.44.225 "md5sum /opt/astro/runtime/<file>.py"
cd F:/astro && md5sum runtime/<file>.py

# Bulk (rare, only when many files changed):
cd F:/astro && tar --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='Books' -czf /tmp/astro_sync.tgz runtime/ engine/ charts/ main.py frontend/
scp -P 22 /tmp/astro_sync.tgz root@46.28.44.225:/tmp/
ssh root@46.28.44.225 "cd /opt/astro && tar -xzf /tmp/astro_sync.tgz && pm2 restart astro-engine"

# PM2 (VPS):
ssh root@46.28.44.225 "cd /opt/astro && pm2 start ecosystem.config.cjs"
```
