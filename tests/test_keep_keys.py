"""A button key that matches a filter-persistence prefix must be excluded in main.py (_BUTTON_KEYS), or the page crashes with 'read-only session state'."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_buttons_are_excluded():
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    prefixes = tuple(re.findall(r'"([a-z_]+)"', re.search(r"_KEEP_PREFIX = \((.*?)\)", src, re.S).group(1)))
    excluded = set(re.findall(r'"([a-z_]+)"', re.search(r"_BUTTON_KEYS = \{(.*?)\}", src, re.S).group(1)))
    skip = ("acc_", "sm_run_", "ac_done")
    bad = []
    for ln in src.splitlines():
        if ".button(" in ln or "st.button(" in ln:
            for k in re.findall(r'key=f?"([^"{]+)', ln):
                if k.startswith(prefixes) and k not in excluded and not k.startswith(skip):
                    bad.append(k)
    assert not bad, f"buttons whose state would be rewritten: {bad}"


if __name__ == "__main__":
    test_buttons_are_excluded(); print("ok keep keys")
