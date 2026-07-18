"""Canonical project root for local (F:/astro) and VPS (/opt/astro)."""
from __future__ import annotations

import os
from pathlib import Path

ATRO_ROOT = Path(os.environ.get("ATRO_ROOT", Path(__file__).resolve().parent))
CHARTS_DIR = Path(os.environ.get("ATRO_CHARTS", ATRO_ROOT / "charts"))
REPORTS_DIR = Path(os.environ.get("ATRO_REPORTS", ATRO_ROOT / "reports"))
EPHE_DIR = Path(os.environ.get("ATRO_EPHE", ATRO_ROOT / "ephe"))
