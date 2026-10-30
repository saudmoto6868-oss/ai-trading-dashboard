# Footprint recorder (مسجّل الفوت برينت)

خدمة صغيرة شغالة طول الوقت: بتسمع صفقات OKX العامة، وبتجمّعها لكل دقيقة × سعر (شراء/بيع)، وبتحفظها 7 أيام، وبتقدّمها للتطبيق كـ JSON. بيانات عامة بس: من غير مفاتيح ولا أوامر ولا بيانات مستخدمين.
A small always-on service: listens to the OKX PUBLIC trades WebSocket, sums prints per minute x price (buy / sell), keeps 7 days in SQLite and serves JSON for the app's footprint. Public data only: no keys, no orders, no user data.

## ليه محتاجينها / why
OKX بيدّي 100 صفقة بس في كل طلب، والبيتكوين فيه آلاف الصفقات كل 5 دقايق: من المتصفح مستحيل ترجع لورا أكتر من شمعتين. المسجّل بيسمع طول الوقت فالتاريخ بيبقى كامل، وبيفتكر **إمتى كان سامع** (أي فجوة تفضل فجوة، مش "مفيش صفقات").
The exchange returns 100 prints per request, so a busy market cannot be walked back in a browser. The recorder listens continuously and remembers WHEN it was listening (a gap stays a gap).

## التشغيل / run
```
pip install -r recorder/requirements.txt
SYMBOLS=BTC-USDT,ETH-USDT,SOL-USDT PORT=8080 DB=fp.sqlite python recorder/footprint_recorder.py
```
أو Docker: `docker build -t fp-recorder recorder && docker run -d -p 8080:8080 -v fpdata:/data -e SYMBOLS=BTC-USDT,ETH-USDT fp-recorder`

## الاستضافة / hosting (المالك يختار؛ مفيش حاجة هنا بتشتغل من غير استضافة)
محتاجة عملية بتفضل شغالة + قرص صغير (SQLite). أي واحدة من دول تنفع (الأسعار بتتغير، اتأكد بنفسك):
- VPS صغير (أي مزوّد): الأسهل، `docker run` وخلاص، شغّله خلف HTTPS (Caddy / nginx) لأن التطبيق على https.
- Fly.io / Railway / Render: من الـ `Dockerfile`، لازم volume للقرص (`/data`) وإلا التاريخ بيضيع عند إعادة التشغيل.
- جهازك البيت: ينفع للتجربة بس مش 24/7.
الحجم تقريبًا: رمز سريع زي BTC حوالي 3 كيلوبايت في الدقيقة (حوالي 20 ميجا في اليوم قبل الضغط)؛ 3 رموز × 7 أيام تعدّي 100 ميجا بشوية.
Needs an always-on process + a small disk volume. Put it behind HTTPS (the app is on https; a plain http URL is rejected by the app).

## ربط التطبيق / connect the app
في Streamlit Secrets (أو متغير بيئة): `FOOTPRINT_SERVER_URL = "https://your-recorder.example.com"`. من غيره التطبيق بيشتغل بمخزن المتصفح لوحده زي دلوقتي.
عند فتح الشارت (فريم دقيقة أو أكبر) التطبيق بيطلب من المسجّل الدقايق الناقصة، وبيعلّم المدى اللي كان المسجّل سامع فيه "كامل". الدقايق على حافة المدى (اللي سمعها جزئي) مش بتتحسب كاملة.

## الواجهة / API
- `GET /fp?sym=BTC-USDT&from=<ms>&to=<ms>` → `{"sym", "cov": [[from, to], ...], "mins": {"<minute ms>": [price, buy, sell, ...]}}` (حد أقصى 72 ساعة في الطلب، gzip لو العميل بيطلبه)
- `GET /health` → الرموز المسجّلة ومن إمتى.
- الرمز لازم يكون في `SYMBOLS` وإلا 404. CORS مفتوح (بيانات سوق عامة للقراءة بس).

## اختبار / tests
`PYTHONPATH=. python tests/test_footprint_recorder.py` (من غير نت: تجميع، فجوات، HTTP، حلقة الـ WebSocket بمقبس وهمي) و`tests/browser/footprint_recorder_client_mock.js` (المتصفح + مسجّل وهمي). **ما اتجربش على OKX الحقيقي ولا على استضافة حقيقية.**
