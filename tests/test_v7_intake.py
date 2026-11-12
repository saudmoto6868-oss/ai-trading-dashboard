"""Schema gate for data/v7 (docs/NEW_TAB_INTAKE_CONTRACT.md section 2.1). Plain script, no network.
Checks shape only: it cannot tell whether a claim is true, and it does not check that URLs are alive."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "v7")
TYPES = {"video", "post", "article", "paper"}
CONF = {"low", "medium", "high"}
STATUS = {"unverified", "measured", "rejected"}
SRC_KEYS = {"id", "title", "url", "type", "author", "published", "fetched", "language", "license_note"}
CLAIM_KEYS = {"id", "source_id", "timestamp_or_locator", "claim", "category", "testable", "how_to_test", "confidence", "status"}
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{30,}|glpat-[A-Za-z0-9_-]{15,})")


def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return json.load(f)


def test_sources():
    S = load("sources.json")
    assert isinstance(S, list) and S, "sources.json must be a non-empty list"
    ids = [s["id"] for s in S]
    assert len(ids) == len(set(ids)), "duplicate source id"
    urls = [s["url"] for s in S]
    assert len(urls) == len(set(urls)), "duplicate source url"
    for s in S:
        miss = SRC_KEYS - set(s)
        assert not miss, (s.get("id"), "missing", miss)
        assert s["type"] in TYPES, (s["id"], s["type"])
        assert s["url"].startswith("https://"), (s["id"], s["url"])
    print("ok sources", len(S))


def test_claims():
    S = {s["id"] for s in load("sources.json")}
    C = load("claims.json")
    assert isinstance(C, list) and C, "claims.json must be a non-empty list"
    ids = [c["id"] for c in C]
    assert len(ids) == len(set(ids)), "duplicate claim id"
    for c in C:
        miss = CLAIM_KEYS - set(c)
        assert not miss, (c.get("id"), "missing", miss)
        assert c["source_id"] in S, (c["id"], "unknown source", c["source_id"])
        assert c["timestamp_or_locator"].strip(), (c["id"], "empty locator")
        assert c["confidence"] in CONF, (c["id"], c["confidence"])
        assert c["status"] in STATUS, (c["id"], c["status"])
        assert isinstance(c["testable"], bool), (c["id"], "testable must be true/false")
        assert c["how_to_test"].strip(), (c["id"], "empty how_to_test")
        assert len(c["claim"]) <= 1200, (c["id"], "claim too long: summarise, do not paste")
    print("ok claims", len(C))


def test_no_secrets():
    for name in ("sources.json", "claims.json", "README.md"):
        with open(os.path.join(D, name), encoding="utf-8") as f:
            assert not SECRET.search(f.read()), (name, "looks like a key / token")
    print("ok no secrets")


if __name__ == "__main__":
    if not os.path.isdir(D):
        print("skip: data/v7 not present on this branch")
        sys.exit(0)
    test_sources(); test_claims(); test_no_secrets()
    print("ALL V7 INTAKE CHECKS PASSED (shape only)")
