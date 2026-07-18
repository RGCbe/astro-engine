"""API key ? subscription tier resolution. Keys come from env only (no client tier spoofing)."""
from __future__ import annotations

import json
import os
from typing import Dict

VALID_TIERS = frozenset({"free", "premium", "professional", "enterprise"})


def _parse_api_keys_env() -> Dict[str, str]:
    """ATRO_API_KEYS: comma-separated key:tier pairs, or JSON object {key: tier}."""
    raw = (os.environ.get("ATRO_API_KEYS") or "").strip()
    registry: Dict[str, str] = {}
    if not raw:
        return registry
    if raw.startswith("{"):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    tier = str(v).strip().lower()
                    if tier in VALID_TIERS:
                        registry[str(k).strip()] = tier
        except json.JSONDecodeError:
            pass
        return registry
    for part in raw.split(","):
        part = part.strip()
        if ":" not in part:
            continue
        key, tier = part.rsplit(":", 1)
        tier = tier.strip().lower()
        if tier in VALID_TIERS:
            registry[key.strip()] = tier
    return registry


def load_api_keys_registry() -> Dict[str, str]:
    registry = _parse_api_keys_env()
    if os.environ.get("ATRO_ALLOW_DEV_KEYS", "").strip() == "1":
        registry.update({
            "atro_free_dev_key": "free",
            "atro_premium_dev_key": "premium",
            "atro_pro_dev_key": "professional",
            "atro_enterprise_dev_key": "enterprise",
        })
    return registry


def resolve_user_tier(data) -> str:
    """Tier from validated api_key only. Ignores client user_tier."""
    api_key = getattr(data, "api_key", None)
    if not api_key:
        return "free"
    registry = load_api_keys_registry()
    return registry.get(api_key, "free")


def cors_allowed_origins() -> list:
    raw = (os.environ.get("ATRO_CORS_ORIGINS") or "").strip()
    if raw == "*":
        return ["*"]
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
