"""Guard: wirefmt stays dependency-free.

Phase 3 firmware implements against wirefmt's schemas and fixtures; the
Python reference must never quietly grow a third-party dependency. Checked
structurally: every import statement in every wirefmt module must target the
stdlib or the package itself.
"""
import ast
import sys
from pathlib import Path

import wirefmt

ALLOWED = set(sys.stdlib_module_names) | {"wirefmt"}
PACKAGE_DIR = Path(wirefmt.__file__).parent


def test_wirefmt_imports_only_stdlib():
    offenders = []
    for py in PACKAGE_DIR.glob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module] if node.module else []
            else:
                continue
            for name in names:
                root = name.split(".")[0]
                if root not in ALLOWED:
                    offenders.append(f"{py.name}: {name}")
    assert not offenders, f"wirefmt must be stdlib-only: {offenders}"
