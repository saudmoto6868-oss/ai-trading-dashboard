"""Free-first PR review: sends a PR's changed files to Gemini and prints the verdict (manual workflow only).

Verdict format asked of the model: one word on the first line (APPROVE / APPROVE_WITH_CHANGES / REJECT), then the
reasons with line numbers. The output is a review opinion, not evidence of a trading edge."""
import json
import os
import sys

import requests

GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GITHUB = "https://api.github.com/repos/{repo}/pulls/{pr}/files"
MODELS = ["gemini-flash-latest", "gemini-2.5-flash"]
CHECKS = ("Check for: contradictory rules, look-ahead (any use of future bars), cost applied on net R, "
          "out-of-sample split fixed before the run, evidence gate (n >= 100, t > 3, both halves positive), "
          "secrets or keys in code, changes to trading logic without tests.")


def build_prompt(title: str, files: list[dict]) -> str:
    parts = [f"PR: {title}", CHECKS,
             "Answer: first line exactly APPROVE, APPROVE_WITH_CHANGES or REJECT. Then up to 6 reasons, each with file and line."]
    for f in files:
        parts.append(f"--- {f.get('filename')} ({f.get('status')})\n{f.get('patch') or '(binary or too large)'}")
    return "\n\n".join(parts)


def fetch_files(repo: str, pr: str, token: str) -> list[dict]:
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    out, page = [], 1
    while True:
        r = requests.get(GITHUB.format(repo=repo, pr=pr), headers=h, params={"per_page": 100, "page": page}, timeout=60)
        r.raise_for_status()
        batch = r.json()
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def ask_gemini(key: str, prompt: str) -> str:
    last = ""
    for m in MODELS:
        r = requests.post(GEMINI.format(model=m), headers={"x-goog-api-key": key, "content-type": "application/json"},
                          json={"contents": [{"parts": [{"text": prompt}]}],
                                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500}}, timeout=300)
        if r.status_code in (404, 429, 503):
            last = f"{m}: HTTP {r.status_code}"
            continue
        r.raise_for_status()
        return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
    raise RuntimeError(last or "no Gemini model answered")


def main() -> int:
    repo, pr = os.environ["REPO"], os.environ["PR"]
    gh, gk = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GEMINI_API_KEY", "")
    if not gk:
        print("GEMINI_API_KEY is empty", file=sys.stderr)
        return 1
    files = [f for f in fetch_files(repo, pr, gh) if f.get("filename", "").endswith(".py")]
    if not files:
        print("no python files in this PR", file=sys.stderr)
        return 1
    title = os.environ.get("TITLE", f"PR {pr}")
    verdict = ask_gemini(gk, build_prompt(title, files))
    print(verdict)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## Gemini review: PR {pr}\n\n{verdict}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
