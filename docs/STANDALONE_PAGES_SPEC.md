# الصفحات المستقلة — مواصفات البناء

> تاريخ: 2026-10-29  
> القرار: 3 صفحات HTML مستقلة، كل واحدة ليها زرار في الـ sidebar يفتحها.  
> المبدأ: خفيفة + منفصلة + تتكامل مع المشروع ولا تحمّله.

---

## الصفحات الثلاث

### 1. `veles_robustness.html` — Veles · Robustness Lab
**مصدر الإلهام:** Veles Quant Desk (صور 3-4 من Threads)  
**الفكرة:** كيف تتصرف الاستراتيجية في أنظمة السوق المختلفة؟

**الأقسام:**
- **Robustness Matrix** — جدول ملون: الصفوف = استراتيجيات، الأعمدة = أنظمة السوق
  - الأنظمة: Trend / Chop / Hi-Vol / Crash / Squeeze / Thin
  - البيانات لكل خلية: avg R، win rate، Sharpe — أخضر/أحمر
- **Live Survivors** — عدد الاستراتيجيات اللي Sharpe > 0 في ≥3 أنظمة
- **Plateau Surface** — 3D surface: Lookback × Threshold × Sharpe (بصري ← Chart.js 3D)
- **Markout Decay** — خط: كيف تتآكل الحافة بعد الـ fill (bps عند 1s/10s/30s/1m/5m/10m/60m)

**حساب تصنيف النظام (من الكاندلز):**
```
Trend:   ADX > 25
Chop:    ADX < 20 AND ATR_ratio < median_ATR
Hi-Vol:  ATR_ratio > 1.5× median_ATR
Crash:   return < -2σ (5-bar window)
Squeeze: BB_width < 20th percentile
Thin:    volume < 20th percentile
```

**البيانات:** `market_cache.get_klines()` → حساب ADX/ATR/BB في JS أو Python endpoint  
**API endpoint:** `GET /api/robustness?symbol=BTC-USDT-SWAP&tf=4h`

---

### 2. `quant_montecarlo.html` — Quant · Monte Carlo
**مصدر الإلهام:** Claude×Quant + Quincunx (صور 9-10 من Threads)  
**الفكرة:** هل الاستراتيجية حقيقية ولا بخت؟

**الأقسام:**
- **Path Simulation** — 7000 مسار على الـ equity curve (bootstrap resample)
  - الخطوط: رمادية شفافة (كل المسارات) + خط الواقع ملون فوقهم
  - Band: 5th–95th percentile ملون
- **Outcome Distribution** — histogram للنتايج النهائية
  - أحمر: تحت رأس المال الأصلي، أخضر: فوقه
  - خط P-value (P < 0.008 = significant)
  - STD Tile: `(E[final] - C0) / std(final)` — رقم واحد كبير
  - Expected: المتوسط، Worst 5%
- **Ruin Probability** — نسبة المسارات اللي عدت 20% drawdown
- **Quincunx · 7 Gates** — Galton board: 7 بوابات، كل واحدة = نسبة الفوز التراكمية
  - الكرات بتنزل left/right بناء على win_rate
  - النتيجة = histogram في الأسفل يطابق التوزيع الثنائي

**الفورميولا الأساسية:**
```python
paths[i] = capital × cumprod(1 + random.choice(trade_returns, N, replace=True))
ruin = any(drawdown > 20%) across path
p_value = fraction(random_paths >= actual_median)
std_tile = (mean(final) - capital) / std(final)
```

**البيانات:** قايمة صفقات من `data/strategy_lab.json` أو إدخال يدوي  
**API endpoint:** `GET /api/montecarlo?strategy=sch_ict&n_paths=7000`

---

### 3. `micro_foundations.html` — Micro · Foundations
**مصدر الإلهام:** Polymarket Bot (صور 12-13) + `docs/INSTITUTIONAL_FOUNDATIONS.md`  
**الفكرة:** عرض البنية الميكروية للسوق وطريقة تفكير المؤسسات

**الأقسام:**
- **Resolution Grid** — شبكة تفاعلية للأسعار المستديرة والـ fills
  - خلايا: كل خلية = مستوى سعري (مثل 85¢/35¢/15¢)
  - اللون: شدة النشاط عند المستوى ده
  - Poll Clock: وقت لحد أقرب fill/expiry
- **Inventory Plane** — scatter plot: Paired vs Residual
  - X = directional bias، Y = residual inventory
  - كل نقطة = صفقة، اللون = الاتجاه
- **Side Chain** — up/down switches مع ladder
  - مخطط دائري (tetrahedron): Bull/Bear/Neutral + transitions
  - Ladder: مستويات الـ entry المرتبة
- **Market Structure** (من INSTITUTIONAL_FOUNDATIONS.md):
  - Order Flow hierarchy: Tier 1 Banks → Prime Brokers → Retail
  - Key levels: تجميع، توزيع، sweep zones

**البيانات:** OKX order book + trades tape (موجود في workspace_app.html)  
**API endpoint:** `GET /api/microstructure?symbol=BTC-USDT-SWAP`

---

## طريقة الربط بالمشروع

### في `main.py` (sidebar):
```python
# بعد كل page في _PAGES
with st.sidebar:
    if st.button("📊 Veles · Robustness"):
        st.components.v1.iframe("/static/veles_robustness.html", height=900, scrolling=True)
```

أو: زرار يفتح URL جديد (أنظف):
```python
st.sidebar.markdown('[📊 Veles Lab](/?page=veles)', unsafe_allow_html=True)
```

### أو كـ Streamlit pages:
```
pages/
  veles_robustness.py   → يخدم الـ HTML
  quant_montecarlo.py
  micro_foundations.py
```

---

## ترتيب البناء

1. **أول:** `quant_montecarlo.html` — الأبسط، pure JS/numpy، مش محتاج بيانات حية
2. **تاني:** `veles_robustness.html` — محتاج candle data (موجود)
3. **تالت:** `micro_foundations.html` — محتاج order book + tape

---

## قواعد الخفة

- كل صفحة ملف HTML واحد (JS + CSS inline)
- البيانات تيجي من endpoint بسيط (`/api/...`) مش من ملفات كبيرة
- مفيش import من modules المشروع — الـ endpoint هو الـ bridge
- Chart.js فقط (موجود في workspace_app.html) — مفيش D3 أو three.js إلا لو ضروري
- الـ endpoint نفسه خفيف: يرجع JSON بس

---

## ملاحظة أمان

لا secrets، لا API keys في الـ HTML — كل بيانات حساسة من الـ backend endpoint فقط.
