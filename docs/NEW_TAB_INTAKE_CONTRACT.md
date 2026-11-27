# New tab intake contract (research data -> a tab in the platform)

Used for the new tab Gemini is building (branch `v7-single-indicator`, created from main, no commits yet on 2026-11-10). Applies to any new tab built from tables an AI produced (videos, Instagram, articles).

## 1. What Gemini delivers (data only, in the repo, no app edits)
One folder `data/<tab>/` with:
- `sources.json`: every source once: `id`, `title`, `url`, `type` (video / post / article / paper), `author`, `published` (date), `fetched` (date), `language`, `license_note`.
- `claims.json` (or `.csv`): one row per claim: `id`, `source_id`, `timestamp_or_locator` (video time / paragraph), `claim` (short, own words), `category`, `testable` (true/false), `how_to_test`, `confidence` (low / medium / high = how clearly the source states it, NOT whether it is true), `status` (`unverified` by default).
- `README.md`: how the table was made and what was NOT covered.
Rules: no invented numbers; a number appears only with its source id + locator; transcripts are summarised, not pasted (copyright); no keys, no personal data.

### 1b. Amendments (2026-11-10, after the V7 review)
- Sources that are files of this repository may be typed `repo` (the `article` type is accepted for the first V7 delivery).
- Rows describing what OUR project does or what the owner asked (categories `project-setting`, `process`, and the backtest figures of our own pipeline) are PROJECT FACTS, not market claims: they are excluded from the "% of claims tested" and are never shown as research results.
- A rule chosen after trying several variants on the same sample is selection-biased: record every variant tried, and pre-register (`docs/PREREG_*.md`) before testing any new one.

## 2. What Claude does with it (review gate before anything shows in the app)
1. Schema check (a plain test script under `tests/`), duplicate / dead-link / missing-locator report.
2. Mark which claims are testable with the platform's own engines (walk-forward lab, order-flow backtest, regime). Untestable claims stay `unverified`, shown as opinions.
3. Tab shows: claim, source + locator, status, and measured result (n, edge vs random) when a test exists. Under n=30: `not evidence`.

## 3. What the tab takes from the platform / gives back
Takes: the symbol and timeframe selected in TIA / Workspace, the Journal results, lab results (`STRATEGY_LAB.md`), regime (`modules/regime.py`), Academy lessons.
Gives back: tested claims become candidate rules for the lab (`pre-registered` in `docs/PREREG_*.md` before running), Academy lesson links, and a `source quality` score per author (how many of their testable claims survived).

## 4. Sustained development + news follow-up
- `sources.json` is append-only; each source has a `fetched` date and a re-check interval (default 90 days).
- News: only public RSS / feeds already used by the platform (no scraping behind logins, no keys in the repo). A scheduled job (the existing GitLab schedule, `main` only) may append headlines to `data/<tab>/news.jsonl` with source + time; nothing is auto-promoted to a claim. A human or reviewer promotes.
- Every change goes through an MR; CI `mr_tests` runs the schema test. Merge only after review.
- The tab states its coverage at the top: number of sources, date range, % of claims tested.

## 5. Not done yet
No data from Gemini is in the repo yet; no tab code exists. This contract is a proposal for the owner / Gemini to accept or change.
