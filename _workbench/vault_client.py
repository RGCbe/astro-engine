"""Thin re-export of api-expense-manager vault_client for _deep_extract."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2] / "api-expense-manager"
if _ROOT.exists():
    sys.path.insert(0, str(_ROOT))

from vault_client import (  # noqa: E402,F401
    checkout_key,
    get_llm_client,
    llm_completion,
    report_usage,
)
