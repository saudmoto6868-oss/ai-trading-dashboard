# V7: المعمارية

## الملفات
| ملف | دوره |
|---|---|
| `modules/v7_page.py` | `render()` (Streamlit): الراديو (Live chart / Snapshot dashboard / Chart images / Rules / Claims & evidence)، `live_html()` بيجمّع صفحة الشارت الحي بحقن الملفات في placeholders، `dashboard_html()` للـ snapshot، `load()/summarize()` لـ `data/v7`. بيعرض بـ `st.iframe(html, height=920, alt=...)`. ممنوع `st.button` وكلمات BUY/SELL/LONG/SHORT في الملف (تست). |
| `modules/v7_live_app.html` | الصفحة الواحدة (HTML+JS): الشريط، القوائم، 4 charts (سعر + osc + macd + extra pane) + `canvas#ov` للرسم، اللوحة الجانبية، i18n. placeholders: `/*LIB*/ /*IND*/ /*STRUCT*/ /*EXTRA*/ /*SMC*/ /*IND2*/ /*CFX*/` (كل `<script>/*X*/</script>`). |
| `modules/v7_live_ind.js` | CFX v7: Stoch 5,3,3 + RSI14 + MACD(12,26,1) + SMA77/144 + القاعدة B (`signalsB`) + `dayPlan`/`sessionNow`/`trendOf`. `window.V7IND`. |
| `modules/v7_live_struct.js` | swings (L=3)، ATR14، EQH/EQL، FVG، BOS/CHoCH، 50%، OTE، sessions (توقيت نيويورك)، prevDay (يوم نيويورك يتقلب 18:00). `V7STRUCT`. |
| `modules/v7_live_extra.js` | VWAP الجلسة، volume profile (POC/VAH/VAL)، opens يوم/أسبوع + أسبوع سابق، kill zones، HH/HL/LH/LL، order blocks، `filterSignals`. `V7EXTRA`. |
| `modules/v7_live_smc.js` | `srZones`، `breakers`، `inverseFvg`، `tradeCandidate` (R>=2). `V7SMC`. |
| `modules/v7_live_ind2.js` | SMA/EMA/Bollinger/Donchian/ATR/Keltner/Supertrend/Ichimoku/ADX/OBV/CCI/Williams. `V7IND2`. |
| `modules/v7_live_cfx.js` | دفعة 1: `obAll` (MIT + نسبة حجم)، `sweeps`، `cisd`، `cisdHtf`، `trendLine`، `pools`، `fibLevels`، `divergences`، `trackCandidate`. `V7CFX`. |
| `tests/test_v7_*.py` | كل دالة JS مقابل تنفيذ بايثون **مستقل** (swings, extra, smc, ind2, cfx, live, dayplan) + `test_v7_live_wiring.py` (الصفحة بتتجمّع، `node --check` لكل سكريبت، `st.iframe` موجود، مفيش `components.html`) + `test_v7_page.py` + `test_v7_intake.py`. |
| `research/cfx/*`, `data/v7/*` | بحث CFX (README, REQUIREMENTS 52 بند, pipeline, Pine, dashboard snapshot) وداتا المصادر/claims. |
| `docs/V7_CFX_AUDIT_2026-11-12.md`, `V7_AGENTS_MASTER_PLAN_2026-11-12.md` | مراجعة 7 صور CFX مقابل المنصة + خطة الـ agents. |

## تدفق الداتا (المتصفح بس، من غير سيرفر)
- OKX: `GET /api/v5/market/candles?instId&bar&limit=300` (index 5 = volume، index 8 = confirm). Hyperliquid: `POST /info {type:'candleSnapshot', req:{coin:'xyz:GOLD', interval, startTime, endTime}}`. قائمة الرموز: OKX `tickers?instType=SPOT` (أعلى 160 USDT) + HL `{type:'meta', dex:'xyz'}`.
- `tick()` كل 5 ثواني: يحمّل، يحسب كل حاجة، يرسم. أول شمعة جديدة => `setData`، غير كده `update` للأخيرة بس (`series.update` بيقبل آخر شمعة أو أحدث فقط - خطأ "Cannot update oldest data" لو اتخالفت).
- الهيكل بيتحسب على **الشموع المقفولة** (`closed`)؛ الشمعة اللي بتتكوّن بتتعرض بس.
- `planTick()` كل 60 ثانية: 1D/4H/1H/15m => `dayPlan` => `LPLAN` => شرائح MTF + العقل المفكر.

## أوامر
```bash
for t in tests/test_v7_*.py tests/test_cfx_rr_policy.py; do PYTHONPATH=. python3 $t || echo FAIL $t; done     # needs node + numpy + tzdata
PYTHONPATH=. python3 -c "from modules import v7_page as V;h,e=V.live_html();assert not e,e;open('/tmp/v7_built.html','w').write(h)"
node docs/v7-development/tools/v7_mock_smoke.js     # Playwright + mocks
```

## فخاخ اتعمل فيها أخطاء قبل كده
- **TDZ:** أي `const/let` (زي `t`, `lang`) لازم يتعرّف قبل أول استخدام؛ كسر القوائم مرة. i18n دلوقتي بعد `const $=`.
- **`LightweightCharts` v4.1.3:** `setMarkers` لازم مرتبة بالوقت؛ whitespace data `{time}` بيقطع الخط (Supertrend بيستخدمه)؛ اتحقق من `update()` كما فوق.
- **`st.iframe` مش بيدعم scrolling=False:** الـ fit بيتم من جوه الـ iframe (`window.frameElement` - same-origin). HTML من كودنا بس، **ممنوع** تمرير HTML من مستخدم/LLM.
- **أي تعديل في `workspace_app.html` يتعمل في `modules/ws/*` ثم `scripts/build_workspace.py`** (قاعدة CLAUDE.md؛ V7 ملفاته مستقلة).
- **`add_commit` على GitLab:** commit كبير ممكن يتعلق على موافقة؛ قسّمه. (دلوقتي الشغل على GitHub بـ git عادي.)
- الشبكة في الـ sandbox مقفولة على مواقع الأسعار: اختبر بـ mocks وقول "mock-tested only".
