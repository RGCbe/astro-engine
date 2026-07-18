# Astro � unified project layout

Single canonical tree on **local** and **VPS**:

| Environment | Path | PM2 service |
|-------------|------|-------------|
| Local (Windows) | `F:\astro` | � |
| VPS (Linux) | `/opt/astro` | `astro-engine` (port 8000) |

## Structure

```
astro/
??? main.py              # FastAPI app entry
??? ecosystem.config.cjs # PM2 config (VPS)
??? ephe/                # Swiss Ephemeris data (VPS; required for charts)
??? venv/                # Python env (VPS only; not synced)
??? runtime/             # Predictors, PDF, translations
??? engine/              # Chart & rule engines
??? frontend/            # Web UI
??? charts/              # Celebrity JSON charts
??? Books/               # Corpus (~1.9 GB)
??? requirements.txt
??? SYNC_LOG.md
??? STATUS.md
??? COORDINATION_PROTOCOL.md
```

## Deploy code to VPS

```powershell
scp -P 22 F:/astro/runtime/<file>.py root@46.28.44.225:/opt/astro/runtime/

cd F:/astro
tar --exclude=__pycache__ --exclude=*.pyc --exclude=venv --exclude=Books --exclude=ephe -czf $env:TEMP\astro_sync.tgz runtime engine charts main.py frontend
scp -P 22 $env:TEMP\astro_sync.tgz root@46.28.44.225:/tmp/
ssh root@46.28.44.225 "cd /opt/astro && tar -xzf /tmp/astro_sync.tgz && pm2 restart astro-engine"
```

## PM2 on VPS

```bash
cd /opt/astro
pm2 start ecosystem.config.cjs
pm2 save
```

## Truth policy (client-facing honesty)

Read **`docs/ENGINE_TRUTH_POLICY.md`**. Live API responses include a `truth` object (mechanical vs cited vs synthesis). Do not use `scratch/` celebrity weights in production.

## API keys & tiers

- Tiers are resolved **only** from `api_key` (see `tier_auth.py`). Client `user_tier` is ignored.
- Set production keys: `ATRO_API_KEYS=your-secret:professional` in `ecosystem.config.cjs` or environment.
- Local dev: `ATRO_ALLOW_DEV_KEYS=1` enables `atro_pro_dev_key` (professional). See `.env.example`.
- UI: open `http://<host>:8000/`, enter API key in the form (stored in session).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `ATRO_ROOT` | Project root (`F:\astro` or `/opt/astro`) |
| `ATRO_API_KEYS` | `key:tier` pairs or JSON map |
| `ATRO_ALLOW_DEV_KEYS` | `1` = include dev keys (local only) |
| `ATRO_CORS_ORIGINS` | Comma-separated origins (default localhost) |
| `ATRO_EPHE` | Swiss Ephemeris directory |

## Disk notes

- Do not restore `_research/repos/` on VPS (was ~13GB of dev git clones).
- Ephemeris must stay at `/opt/astro/ephe`.
- Removed from VPS: `wine-stable`, `video-decoder`, old `astro_backup_*`.
