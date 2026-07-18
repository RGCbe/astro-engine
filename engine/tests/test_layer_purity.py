"""Architectural layering enforcement (restructure 2026-07-18).

The layer manifest lives in docs/architecture/layers.json. The foundation
layer (L0) is the verified astronomy/math core everything else stands on, so
its MODULE-LEVEL imports may only touch the standard library, the ephemeris,
or other L0 modules. Lazy imports inside functions are permitted (e.g.
divisional_charts.analyze_* citing books) — they do not poison import time.

If this test fails, either the new dependency belongs in a higher layer, or
the file's layer assignment in layers.json must be consciously changed.
"""
from __future__ import annotations

import ast
import json
import os
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MANIFEST = os.path.join(_ROOT, "docs", "architecture", "layers.json")

_STDLIB_OK = {
    "__future__", "argparse", "calendar", "collections", "dataclasses", "datetime",
    "enum", "functools", "hashlib", "http", "itertools", "json", "math", "os",
    "pathlib", "random", "re", "socket", "sys", "time", "typing", "unicodedata",
    "urllib", "warnings", "zoneinfo",
}
_EXTERNAL_OK = {"swisseph", "requests"}


def _module_level_imports(path: str) -> set[str]:
    tree = ast.parse(open(path, encoding="utf-8").read())
    found: set[str] = set()
    for node in tree.body:  # top level only — lazy imports are allowed
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


class FoundationPurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.load(open(_MANIFEST, encoding="utf-8"))["layers"]
        cls.foundation = sorted(f for f, layer in manifest.items() if layer == "L0_foundation")
        cls.foundation_basenames = {os.path.basename(f)[:-3] for f in cls.foundation}

    def test_manifest_exists_and_foundation_is_nonempty(self):
        self.assertTrue(self.foundation, "layers.json must define L0_foundation files")

    def test_foundation_modules_import_only_foundation_or_stdlib(self):
        violations = []
        for rel in self.foundation:
            path = os.path.join(_ROOT, rel)
            if not os.path.exists(path):
                violations.append(f"{rel}: file missing but listed in manifest")
                continue
            for imp in _module_level_imports(path):
                root = imp.split(".")[0]
                leaf = imp.split(".")[-1]
                if root in _STDLIB_OK or root in _EXTERNAL_OK:
                    continue
                if root in self.foundation_basenames or leaf in self.foundation_basenames:
                    continue
                if root == "engine" and leaf in self.foundation_basenames:
                    continue
                violations.append(f"{rel}: imports '{imp}' (outside L0)")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
