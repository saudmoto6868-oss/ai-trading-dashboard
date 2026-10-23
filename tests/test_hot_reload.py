"""modules/hot_reload.py: a module copy missing a needed name or parameter is reloaded; a current one is left alone."""
import os, sys, tempfile, importlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import hot_reload as H  # noqa: E402


def test_stale_and_refresh():
    d = tempfile.mkdtemp(); sys.path.insert(0, d)
    f = os.path.join(d, "fakemod_hr.py")
    open(f, "w").write("def class_symbols(cls, top=30):\n    return top\n")
    import fakemod_hr
    assert H.stale(fakemod_hr, ("class_symbols",), None) is False
    assert H.stale(fakemod_hr, ("class_symbols", "newthing")) is True                       # a needed attribute is missing
    assert H.stale(fakemod_hr, (), ("class_symbols", "wide")) is True                       # a needed parameter is missing
    open(f, "w").write("def class_symbols(cls, top=30, wide=False):\n    return (top, wide)\ndef newthing():\n    return 1\n")
    importlib.invalidate_caches()
    done = H.refresh({"fakemod_hr": fakemod_hr}, {"fakemod_hr": ("class_symbols", "newthing")}, {("fakemod_hr", "class_symbols"): "wide"})
    assert done == ["fakemod_hr"] and fakemod_hr.newthing() == 1 and fakemod_hr.class_symbols("x") == (30, False)
    assert H.refresh({"fakemod_hr": fakemod_hr}, {"fakemod_hr": ("class_symbols", "newthing")}, {("fakemod_hr", "class_symbols"): "wide"}) == []   # current copy: nothing to do


def test_real_modules_are_current():
    for name in H.NEED:
        importlib.import_module(name)
    assert H.refresh() == []                                                                 # the shipped modules satisfy their own list


def test_pyc_signal():
    sys.dont_write_bytecode = False                                                    # the check reads the .pyc, so this test needs it written
    d = tempfile.mkdtemp(); sys.path.insert(0, d)
    f = os.path.join(d, "fakemod_pyc.py")
    open(f, "w").write("X = 1\n")
    import fakemod_pyc
    mods = {"modules.fakemod_pyc": fakemod_pyc}
    assert H.compiled_from_older_source(fakemod_pyc) is False                          # just imported: the .pyc matches the source
    open(f, "w").write("X = 2\n")
    os.utime(f, (os.path.getmtime(f) + 5, os.path.getmtime(f) + 5))                    # the source changed after the import
    assert H.compiled_from_older_source(fakemod_pyc) is True
    assert H.refresh_changed("modules.", mods) == ["modules.fakemod_pyc"] and fakemod_pyc.X == 2
    assert H.compiled_from_older_source(fakemod_pyc) is False                          # reloaded: current again


if __name__ == "__main__":
    test_stale_and_refresh(); test_real_modules_are_current(); test_pyc_signal(); print("ok hot reload")
