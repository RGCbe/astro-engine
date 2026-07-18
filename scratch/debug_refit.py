import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.tier_refit import per_lord_lr
import json

data = per_lord_lr("CHILDREN_BORN")
print(json.dumps(data, indent=2))
