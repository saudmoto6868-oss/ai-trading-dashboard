"""CFX target filter must enforce the owner-approved minimum R:R of 1:2."""
import importlib.util
import os
import re
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, "research", "cfx", "cfx_pipeline.py")
LIB = os.path.join(ROOT, "research", "cfx", "cfx_lib.py")


def load_pipeline():
    # cfx_pipeline only needs these research constants/functions at import time.
    fake = types.ModuleType("fused_oscillator")
    for name, value in {
        "COOLDOWN_BARS_15M": 1, "CONSENSUS": 1, "GOLDEN_POCKET": (0.62, 0.79),
        "MIN_LEG_ATR": 1.0, "OTE": (0.62, 0.79), "SPREAD_USD": 0.30,
        "in_killzone": lambda *_a, **_k: False, "hook_flags": lambda *_a, **_k: {},
    }.items():
        setattr(fake, name, value)
    sys.modules["fused_oscillator"] = fake
    spec = importlib.util.spec_from_file_location("cfx_pipeline_policy_test", PIPE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cfx_rr_gate_is_two_to_one():
    module = load_pipeline()
    assert module.RR1_MIN == 2.0
    tp1, tp2 = module.apply_rr_gate(
        [(115.0, "1.5R"), (120.0, "2R"), (130.0, "3R")],
        "long", 100.0, 10.0,
    )
    assert tp1 == (120.0, "2R", 2.0), tp1
    assert tp2 == (130.0, "3R", 3.0), tp2
    assert module.apply_rr_gate([(115.0, "1.5R")], "long", 100.0, 10.0) == (None, None)


def test_cfx_library_uses_same_rr_minimum():
    source = open(LIB, encoding="utf-8").read()
    match = re.search(r"^RR1_MIN\\s*=\\s*([0-9.]+)", source, flags=re.M)
    assert match and float(match.group(1)) == 2.0, "cfx_lib RR1_MIN must match cfx_pipeline"


if __name__ == "__main__":
    test_cfx_rr_gate_is_two_to_one()
    test_cfx_library_uses_same_rr_minimum()
    print("ok CFX enforces minimum 1:2 R:R in pipeline and library")
