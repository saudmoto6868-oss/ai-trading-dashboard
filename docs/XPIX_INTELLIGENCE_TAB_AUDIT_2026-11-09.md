# XPIX Intelligence — Tab Runtime Audit & Proposal
Date: 2026-11-09
Branch: `feat/xpix-intelligence-workspace`
Status: REVIEW FINDINGS / PROPOSAL ONLY

## Owner constraints
- Do not change the number, names, order, or grouping of the existing XPIX Intelligence tabs without explicit owner approval.
- Do not expose Meeting Room / internal agent coordination in the public product UI. Meeting notes, decisions, handoffs and archives remain repository-internal.
- This document records findings and proposed work. It does not authorize a tab redesign.

## Confirmed code observations

### Shared data path
- `modules/ws/22x_intelligence.js` subscribes to `Hub.sub("book", symbol, ...)` and `Hub.sub("trades", symbol, ...)`; it does not create its own polling loop.
- `modules/ws/15_ws_hub_indicators.js` owns the shared Hub polling. Book/trades are refreshed on a 1.5-second timer and published to subscribers.
- The Hub book payload currently contains `bids`, `asks`, and `deep`, but no timestamp field.
- The Hub trades payload contains `rows`, `all`, `hits`, `ab`, `abDir`, and `stats`, but no top-level timestamp field.
- Consequently, the Intelligence panel's `age(book)` / `age(tape)` helper cannot calculate age: it looks for `.t` and always falls back to “timestamp unavailable”. This is a real data-contract mismatch, not a tab-layout issue.
- Yahoo-backed `Y:` symbols deliberately return “no order book / tape for this market”; this should be shown as unsupported source coverage, not a generic feed failure.
- The Hub uses OKX public order book and recent trades for supported OKX instruments. This is one venue's view, not consolidated/global liquidity.

### Tab-by-tab state

| Existing tab | What the current code actually does | Confirmed gap | Proposed direction (no implementation yet) |
|---|---|---|---|
| Overview | Mid from best bid/ask; buy/sell volume and delta from current Hub trade rows; top-10 bid/ask size; data status; shortcuts | Freshness is unavailable because payload timestamps are absent; KPI cards have no visual history/context | Add source/venue/freshness badges, spread, imbalance, short rolling history and clear unsupported/stale states |
| Order Flow | Aggregates buy/sell volume from the latest Hub trade snapshot and calculates net delta | Not a real footprint view; no per-price ladder, candle delta, stacked imbalance, cumulative delta or session context in this tab | Reuse existing Footprint and Tape calculations; show price-level bid/ask ladder and delta visuals, with timeframe/session controls only if owner approves |
| Liquidity | Top-10 displayed bid/ask size; shortcuts to OFM, DOM and Limit Tracker | No heatmap rendered inside this tab; displayed size alone is not liquidity evolution | Reuse OFM snapshots and DOM data; visualize depth by price/time, additions/pulls and caveat venue coverage |
| Auction / Volume | Opens chart/Volume Profile and multi-timeframe value-level panels | The tab itself contains no POC/VAH/VAL, value area, acceptance/rejection or profile visualization | Embed/reuse existing Volume Profile outputs; show POC, VAH, VAL, value migration and session context |
| Setups | Explicit WAIT state and opens existing Setup Card | No XPIX deterministic ranked setup engine or evidence packet is connected yet | Keep WAIT until rule engine exists; show Setup 1/2/3 with evidence, missing conditions, trigger, invalidation, stop/targets, expiry and quality gate |
| Indicators | Opens linked chart and explanatory placeholder | No indicator registry, active-state, parameter, timeframe or signal mapping is connected | Map existing chart indicators and saved settings; show status, source timeframe, last value/signal and conflicts without treating indicators as independent votes |

## Additional integration checks
- `Panel.prototype.build` dispatches by `build_<type>`; the intelligence panel is added through the Workspace panel menu and categorized under Decision in the Snap layout menu.
- The Intelligence panel's symbol-change path re-subscribes to shared Hub book/trades; no independent polling was found in its implementation.
- Existing DOM, Tape and OFM panels already consume the same Hub feeds. Reuse their established renderers/calculations rather than duplicating data acquisition.
- Footprint has a separate historical/recovery path and is attached to chart state; integration needs a defined chart/timeframe handoff and must preserve its existing storage/dedup logic.
- No browser runtime, mobile rendering, generated bundle, or test suite was executed as part of this read-only audit.

## Recommended implementation order (proposal)
1. Fix and test the Hub evidence envelope: source/venue, exchange timestamp, received timestamp, symbol, supported capabilities, and explicit stale/error states. Do not infer freshness from render time.
2. Add contract tests for book/trade payload shape and symbol switching; verify one shared subscription per active feed and cleanup on panel close.
3. Integrate Footprint into Order Flow using existing aggregation, dedup and history logic; validate against the standalone Footprint panel.
4. Integrate OFM/DOM depth snapshots into Liquidity; label venue and distinguish resting liquidity from executed volume.
5. Integrate Volume Profile outputs into Auction / Volume without duplicating its calculations.
6. Map chart indicator registry and saved settings into Indicators.
7. Implement deterministic setup ranking and a versioned decision packet only after evidence contracts and replay tests are ready.
8. Run build check, unit tests, browser tests and desktop/mobile verification before considering a merge.

## Explicitly not authorized
- No tab count/name/order/grouping changes.
- No removal or replacement of existing Workspace tools.
- No generated bundle edits by hand.
- No merge to main, deployment, or live trading actions.


## تنفيذ المراحل 1–7 — تحديث 2026-11-09

- بدأ التنفيذ على الفرع الحالي دون تغيير عدد التابات أو أسمائها أو ترتيبها.
- **1 — Evidence envelope:** أضيفت بيانات `symbol/venue/source/exchangeTs/receivedAt/t/capability` إلى book وtrades من OKX، مع تمييز Yahoo كـ `unsupported` بدل عرضه كأنه عطل اتصال. `receivedAt` هو وقت استلام التطبيق؛ `exchangeTs` لا يُعرض كوقت موثوق إلا عندما يرجعه المصدر.
- **2 — Contract checks:** لم تُضف اختبارات آلية بعد؛ يلزم اختبار payload shape وتبديل الرمز وتنظيف الاشتراكات.
- **3 — Footprint / Order Flow:** لم يتم دمج footprint داخل التاب؛ يلزم أولاً إثبات parity مع أداة Footprint الحالية ومنع ازدواج التجميع.
- **4 — Liquidity:** لم يتم دمج heatmap/DOM داخل التاب؛ سيظل عرض الدفتر موصوفاً كسيولة معروضة من venue واحد.
- **5 — Auction / Volume Profile:** لم يتم نقل POC/VAH/VAL إلى التاب؛ المصدر الحالي هو لوحة Value Levels القائمة.
- **6 — Indicators registry:** لم يتم ربط سجل المؤشرات وإعداداتها؛ لا تُعرض أسماء أو حالات غير مثبتة.
- **7 — Deterministic setup ranking:** لم يتم تفعيل ترتيب فرص أو تنبيهات دخول؛ WAIT يظل الوضع الآمن حتى اكتمال الأدلة والتحقق.
- لا build أو browser test أو CI أو merge أو deploy في هذه الخطوة.


## تحديث المرحلة 2 — 2026-11-09

- أُضيف `tests/browser/xpix_evidence_contract_mock.js` للتحقق من عقد بيانات Hub للـbook والـtrades، ووجود exchange timestamp وreceived timestamp، وتمييز Yahoo كـunsupported.
- الاختبار يدخل تلقائياً ضمن `tests/browser/run_all.sh` لأنه يلتقط كل `*_mock.js`.
- لم يُشغّل محلياً أو على CI بعد؛ الإضافة موجودة على الفرع فقط، ولا تُسجل كاختبار ناجح.
- توضيح CI: `.gitlab-ci.yml` يقيّد GitLab pipeline إلى `schedule` أو `web` فقط؛ لذلك push pipeline الذي ظهر Failed بلا jobs لا يثبت فشل كود XPIX، لكنه أيضاً لا يقدم أي تحقق ناجح.
