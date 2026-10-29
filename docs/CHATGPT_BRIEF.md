# Brief for any external AI (ChatGPT / Gemini / DeepSeek) working on XPIX

Read first: CLAUDE.md, PROJECT_STATUS.md (rows 25 and 26 and the last change-log lines), docs/PIPELINE.md, docs/PLAYBOOKS.md, docs/SCHOOLS.md.

## Rules (non-negotiable)
- Owner: Saud. Answer in Egyptian Arabic when talking to him, short. Code and docs in English.
- Never invent prices, win rates or results. Under n = 30 it is "not evidence". Say what was NOT tested.
- Evidence gate for any rule that goes live: n >= 100, t > 3 vs random direction, positive in BOTH halves (in-sample and out-of-sample). Costs are not in the lab yet.
- Secrets only in Streamlit Secrets / GitHub Secrets. Never commit or print keys.
- Do not edit STRATEGY_LAB.md by hand (the lab writes it). Do not set APP_PASSWORD / APP_USERS (auth is off until launch).
- Push to `main` only through the owner's approval; prefer a branch + review for anything risky.

## Where things are
- Streamlit app: main.py. Workspace (the chart and widgets): modules/workspace_app.html (very long lines: grep, never dump).
- Signals and detectors: modules/signals.py. Harmonic: modules/harmonic.py. Scorer: modules/scorer.py.
- Strategy lab (every school on real candles, random baseline, exit variants, chain grades): modules/strategy_lab.py, results in STRATEGY_LAB.md and data/strategy_lab.json.
- Journal export (CSV) and performance: modules/perf_report.py.
- Tests: `for t in tests/test_*.py; do python3 $t; done`.

## تحديث التنسيق — 2026-10-29 (من Claude — حساب Mohamed)

### اللي اتعمل دلوقتي (لا تكرره):
- **commit 6c7c5a7** — 3 تابات Stats جديدة: Edge Map + Robustness Matrix + Execution Cycle
  - ملفات جديدة: `modules/edge_map_app.html`, `robustness_app.html`, `execution_app.html`
  - Python wrappers: `modules/quant_edgemap.py`, `quant_robustness.py`, `quant_execution.py`
  - `main.py`: segmented_control بقت 6 تابات بدل 3
  - `modules/i18n.py`: ترجمات عربية للتابات الجديدة
- **mock data فقط** — القيم الحقيقية تيجي من lab run (GitHub Actions)

### لا تلمس:
- `modules/workspace_app.html` (شغل Order Flow جاري — PR #63 و#67 draft)
- `data/strategy_lab.json` (الـ lab يكتبها وحده)
- أي PR مفتوح بدون أمر مالك منفصل

### الأولوية الجاية (من docs/PRIORITIES.md):
- **Priority 2:** GitHub Actions lab run — GEMINI_API_KEY موجود في Secrets — محتاج trigger من المالك
- **Priority 4:** Chart bugs — محتاجة browser حقيقي (المالك يشغّله)

### ايه اللي ممكن تساعد فيه:
1. **Code review للتابات الجديدة:** راجع HTML/JS في الملفات التلاتة — أي bug أو تحسين UI
2. **lab run analysis:** لما المالك يشغل GitHub Actions، حلّل النتايج في STRATEGY_LAB.md
3. **اقتراح pair-tests** (موجود في "What we need from you" تحت)

---

## Current state (2026-10-19)
- Item 25 (A+++ pipeline): chain model in docs/PIPELINE.md; lab grades signals 5 layers; playbooks per style; schools mapped in docs/SCHOOLS.md.
- Only the `level` detector (price action) passes the edge gate so far (n ~3150, +0.08R vs -0.02R random).
- Journal (old export, 9 days, 1122 trades): -155R, win 34.5% vs 40% break-even at 1.5R. Scalps on 1m lost -151R (off by default). Intraday longs on 1h were positive (+18R, small sample).
- Exit variants (RR 1.0 / 1.5 / 2.0 / 3.0 and break-even) are being tested on the same entries; the result is pending in GitHub Actions.
- Harmonic is in the lab (key `harmonic`); SMT is not yet (needs peer candles).
- Chart: setups far from price show a waiting label; the full plan draws when price touches the entry; the view is kept after refresh; screenshot and video buttons; widget lock button. Not tested in a real browser.

## What we need from you (pick one task at a time, report back with evidence)
1. Review the school notes in docs/SCHOOLS.md: find published out-of-sample studies (not blogs) for each school and say which claims are testable.
2. Propose at most 3 pair-tests (two detectors or one detector + one context layer) with a pre-stated pass rule, to be run in the lab.
3. Check our code for look-ahead bias (any use of a future candle at decision time) in modules/strategy_lab.py and modules/signals.py. Report line numbers.
