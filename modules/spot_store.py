"""Spot desk storage (owner 2026-11-06: 'online and saved').

Two backends, same interface:
  local   data/spot/ on the server disk (default; Streamlit Cloud can wipe it on a restart)
  github  a PRIVATE GitHub repository used as the online store: ledger.json + files/<id>_<name>.
          Every save is a commit = full history / audit trail; the Telegram bot and the Mac backup read the same place.
Secrets (Streamlit Secrets or env, never in the repo):
  SPOT_GH_TOKEN   fine-grained token with Contents: read + write on that ONE repo only
  SPOT_GH_REPO    e.g. "saudmoto6868-oss/xpix-spot-data" (create it as Private, empty)
  SPOT_GH_BRANCH  optional, default "main"
When SPOT_GH_TOKEN + SPOT_GH_REPO exist the github backend is used automatically."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent / "data" / "spot"
GH = "https://api.github.com"


def _secret(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        try:
            import streamlit as st
            v = str(st.secrets.get(name, "") or "")
        except Exception:
            v = ""
    return v.strip()


def safe_name(name: str) -> str:
    """File name with no path parts and only safe characters."""
    n = "".join(c for c in Path(str(name)).name if c.isalnum() or c in "._-")[-100:]
    return n or "file"


class LocalStore:
    kind = "local"

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else ROOT
        self.files = self.root / "files"

    def describe(self) -> str:
        return f"local disk ({self.root})"

    def load(self) -> dict | None:
        p = self.root / "ledger.json"
        return json.loads(p.read_text(encoding="utf8")) if p.exists() else None

    def save(self, d: dict, msg: str = "") -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        tmp = self.root / "ledger.json.tmp"
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf8")
        tmp.replace(self.root / "ledger.json")   # atomic: never a half-written ledger

    def put_file(self, name: str, data: bytes) -> str:
        self.files.mkdir(parents=True, exist_ok=True)
        n = safe_name(name)
        (self.files / n).write_bytes(data)
        return n

    def get_file(self, name: str) -> bytes | None:
        p = self.files / safe_name(name)
        return p.read_bytes() if p.exists() else None

    def delete_file(self, name: str) -> None:
        try:
            (self.files / safe_name(name)).unlink()
        except FileNotFoundError:
            pass

    def list_files(self) -> list[str]:
        return sorted(p.name for p in self.files.iterdir()) if self.files.exists() else []


class GitHubStore:
    """Private repo as a store via the Contents API (files up to ~50 MB each are fine for invoices)."""
    kind = "github"

    def __init__(self, token: str, repo: str, branch: str = "main", session=None):
        self.repo, self.branch = repo, branch or "main"
        self.s = session or requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
        self._sha: dict = {}

    def describe(self) -> str:
        return f"GitHub private repo {self.repo} ({self.branch})"

    def _url(self, path: str) -> str:
        return f"{GH}/repos/{self.repo}/contents/{path}"

    def _get(self, path: str) -> bytes | None:
        r = self.s.get(self._url(path), params={"ref": self.branch}, timeout=20)
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise RuntimeError(f"GitHub store HTTP {r.status_code} on {path}")
        meta = r.json()
        self._sha[path] = meta.get("sha")
        if meta.get("content") and meta.get("encoding") == "base64":
            return base64.b64decode(meta["content"])
        raw = self.s.get(self._url(path), params={"ref": self.branch}, headers={"Accept": "application/vnd.github.raw"}, timeout=60)   # > 1 MB
        raw.raise_for_status()
        return raw.content

    def _put(self, path: str, data: bytes, msg: str) -> None:
        body = {"message": msg or f"spot: update {path}", "content": base64.b64encode(data).decode(), "branch": self.branch}
        if path not in self._sha:
            self._get(path)
        if self._sha.get(path):
            body["sha"] = self._sha[path]
        r = self.s.put(self._url(path), json=body, timeout=60)
        if r.status_code == 409 or r.status_code == 422:   # someone else saved in between: refuse instead of overwriting
            self._sha.pop(path, None)
            raise RuntimeError("the online ledger changed since it was loaded (another device / the bot); reload the page and redo the change")
        if r.status_code not in (200, 201):
            raise RuntimeError(f"GitHub store HTTP {r.status_code} on {path}")
        self._sha[path] = r.json().get("content", {}).get("sha")

    def load(self) -> dict | None:
        b = self._get("ledger.json")
        return json.loads(b.decode("utf8")) if b else None

    def save(self, d: dict, msg: str = "") -> None:
        self._put("ledger.json", json.dumps(d, ensure_ascii=False, indent=1).encode("utf8"), msg or "spot: ledger update")

    def put_file(self, name: str, data: bytes) -> str:
        n = safe_name(name)
        self._put(f"files/{n}", data, f"spot: file {n}")
        return n

    def get_file(self, name: str) -> bytes | None:
        return self._get(f"files/{safe_name(name)}")

    def delete_file(self, name: str) -> None:
        path = f"files/{safe_name(name)}"
        if path not in self._sha and self._get(path) is None:
            return
        r = self.s.delete(self._url(path), json={"message": f"spot: delete {path}", "sha": self._sha[path], "branch": self.branch}, timeout=30)
        if r.status_code not in (200, 404):
            raise RuntimeError(f"GitHub store HTTP {r.status_code} deleting {path}")
        self._sha.pop(path, None)

    def list_files(self) -> list[str]:
        r = self.s.get(self._url("files"), params={"ref": self.branch}, timeout=20)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return sorted(x["name"] for x in r.json() if x.get("type") == "file")


def get_store():
    tok, repo = _secret("SPOT_GH_TOKEN"), _secret("SPOT_GH_REPO")
    if tok and repo:
        return GitHubStore(tok, repo, _secret("SPOT_GH_BRANCH") or "main")
    return LocalStore()
