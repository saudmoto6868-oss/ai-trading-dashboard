"""scripts/x77_add.py saves a picture / note with school tags, and js_config counts them per school. Run: python3 tests/test_x77_add.py"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

with tempfile.TemporaryDirectory() as t:
    os.environ["X77_DATA_DIR"] = str(Path(t) / "x77")
    import x77_add  # noqa: E402
    from modules import x77_detect  # noqa: E402

    png = Path(t) / "shot.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
    it = x77_add.main(["--file", str(png), "--schools", "S_SMC_ICT,S_FIB", "--sym", "XAUUSD", "--tf", "1h", "--text", "سويب ثم OTE"])
    assert it["kind"] == "image" and it["media"] and "s_smc_ict" in it["tags"] and "chat" in it["tags"], it
    it2 = x77_add.main(["--text", "ملاحظة", "--schools", "s_smc_ict"])
    assert it2["kind"] == "lesson", it2
    try:
        x77_add.main(["--text", "x", "--schools", "S_NOPE"])
        raise AssertionError("bad school accepted")
    except SystemExit as e:
        assert "unknown school" in str(e)
    lib = x77_detect.js_config()["lib"]
    assert lib == {"S_SMC_ICT": 2, "S_FIB": 1}, lib
print("x77_add: passed")
