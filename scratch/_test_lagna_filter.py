#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.lagna_filter import rule_applies_to_lagna  # noqa: E402

assert rule_applies_to_lagna("Mars in 5th gives children.", "Sagittarius")
assert not rule_applies_to_lagna("For Scorpio lagna Mars is bad.", "Sagittarius")
assert rule_applies_to_lagna("For Sagittarius lagna Mars as 5th lord is auspicious.", "Sagittarius")
print("lagna_filter OK")
