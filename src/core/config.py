import os
import json
from typing import Dict, List

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOGIC_BASE_DIR = os.path.join(BASE_DIR, "logic_base")
CORPUS_DIR = os.path.join(BASE_DIR, "gemma_extractions")

# Engine Rule Paths
RULE_ENGINE_PATH = os.path.join(LOGIC_BASE_DIR, "rule_engine.json")

# Default values
DEFAULT_TZ_HOURS = 5.5

# Load Rule Engine (metadata: signs, nakshatras, dasha meanings)
with open(RULE_ENGINE_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)

# Pre-load the multi-book corpus (13,025 deduplicated rules from 19 books)
from engine.corpus import get_corpus as _load_corpus
CORPUS = _load_corpus(CORPUS_DIR)

# CORS Config
def get_cors_origins() -> List[str]:
    raw = (os.environ.get("ATRO_CORS_ORIGINS") or "").strip()
    if raw == "*":
        return ["*"]
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

# API Keys and Tiers
VALID_TIERS = frozenset({"free", "premium", "professional", "enterprise"})

def get_api_keys() -> Dict[str, str]:
    raw = (os.environ.get("ATRO_API_KEYS") or "").strip()
    registry: Dict[str, str] = {}
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
            
    if os.environ.get("ATRO_ALLOW_DEV_KEYS", "").strip() == "1":
        registry.update({
            "atro_free_dev_key": "free",
            "atro_premium_dev_key": "premium",
            "atro_pro_dev_key": "professional",
            "atro_enterprise_dev_key": "enterprise",
        })
    return registry
