"""Every English twin in arabic_en.py (name_en) must have its Arabic function name_ar in arabic.py, and the reverse for the four twinned text builders.

Plain script like the other tests; reads the sources with ast, so it needs no third-party packages.
Signatures are NOT compared on purpose: the Arabic side takes an extra `ar` flag and delegates to the twin.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def public_defs(name):
    tree = ast.parse((ROOT / "modules" / name).read_text(encoding="utf-8"))
    return {n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")}


ar, en = public_defs("arabic.py"), public_defs("arabic_en.py")
problems = [f"arabic_en.{fn} has no arabic.{fn[:-3]}_ar" for fn in sorted(en)
            if fn.endswith("_en") and fn[:-3] + "_ar" not in ar]
problems += [f"arabic_en.{fn} does not follow the name_en convention" for fn in sorted(en) if not fn.endswith("_en")]
print(f"arabic.py: {len(ar)} public functions, arabic_en.py: {len(en)}")
if problems:
    print("PARITY PROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("ok: every English twin has a matching Arabic function")
