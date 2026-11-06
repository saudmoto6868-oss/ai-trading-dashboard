# ربط n8n / Telegram / Claude بالـ XPiX Agent (الخطوة 4)

الـ Agent بيشتغل على الماك ومعاه سيرفر HTTP صغير (`tools/xpix_agent/server.js`). n8n بينده عليه بـ HTTP Request. **الكود ده اتختبر بـ stub + على Streamlit الحقيقي في السحابة من غير أسعار؛ ما اتجربش مع n8n حقيقي.**

## تشغيل (على الماك)
```
streamlit run main.py                                   # المنصة
export XPIX_AGENT_TOKEN="$(openssl rand -hex 24)"       # توكن طويل عشوائي: في env بس، مش في الكود ولا الشات
node tools/xpix_agent/server.js --out ~/xpix_out        # http://127.0.0.1:8765  (يرفض يشتغل من غير توكن)
```
- السيرفر على `127.0.0.1` بس. n8n لو على نفس الماك يوصله مباشرة. لو n8n في السحابة: **ما تفتحش البورت للإنترنت**؛ استخدم نفق مؤمّن (Tailscale أو Cloudflare Tunnel مع Access) أو شغّل n8n على الماك.
- لو أي حد شاف التوكن في شات أو لوج: غيّره (اعمل توكن جديد وأعد التشغيل).

## الواجهة
كل الطلبات: `Authorization: Bearer <XPIX_AGENT_TOKEN>`.
| طلب | شرح |
|---|---|
| `GET /health` | بيرجّع قايمة الأوامر المسموحة |
| `POST /cmd` `{"cmd":"tf","args":["15m"]}` | أمر واحد |
| `POST /batch` `[{"cmd":"page","args":["workspace"]},{"cmd":"symbol","args":["HL:xyz:GOLD"]},{"cmd":"shot","opts":{"out":"gold.png"}}]` | أوامر ورا بعض (بتقف عند أول خطأ) |
| `GET /files/<اسم>.png|mp4` | تحميل لقطة/فيديو اتعمل |

الأوامر: `pages page state list symbol tf toggle addpanel closepanel params set layout draw cleardrawings shot record recstart recstop wait` (نفس الـ CLI؛ التفاصيل في `tools/xpix_agent/README.md`). `opts` اختيارية: `panel`, `out` (اسم ملف بس), `full`, `workspace`, `fps`, `size`, `crf`.
الرد على `shot` / `record` فيه `"file": "/files/gold.png"`.

## حدود الأمان (مبنية في السيرفر)
- توكن إجباري (16 حرف على الأقل) ومقارنة ثابتة الزمن؛ 401 من غيره.
- قايمة أوامر ثابتة: قراءة وعرض ورسم بس. مفيش أوامر صفقات ولا مفاتيح، ومفيش `eval`.
- الملفات بتتكتب وتتقرا من فولدر الإخراج بس (الاسم `[A-Za-z0-9._-]` + `.png|.mp4`)، وأي مسار تاني بيتحول لاسم تلقائي.
- أمر واحد في المرة (طابور)، 60 طلب/دقيقة، حجم الطلب 64KB، `record` أقصى 600 ثانية.

## n8n: إعداد عقدة HTTP Request
- Method `POST`, URL `http://127.0.0.1:8765/cmd` (أو `/batch`), Authentication: Header Auth (`Authorization` = `Bearer <التوكن>`; خزّنه في Credentials مش في الـ workflow).
- Body: JSON. لتحميل اللقطة: عقدة تانية `GET /files/gold.png` بـ Response Format = File، وبعدها Telegram → Send Photo (أو Send Video للـ mp4).
- مثال سلسلة: Telegram Trigger ("/gold") → HTTP `/batch` (page workspace + symbol + tf + shot) → HTTP `GET /files/...` → Telegram Send Photo. **اتحقق من القواعد: الرد لـ chat id بتاع المالك بس.**

## أدوات جاهزة للماك (الخطوة 6)
- **`sh tools/xpix_agent/selftest.sh`**: أمر واحد يجرّب كل حاجة على بياناتك الحية (صفحات، فريم، رمز دهب وBTC، مؤشر MSB، إعداد، رسم، سكرين شوت) ويطبع PASS/FAIL لكل خطوة. **ده اللي يأكد `symbol` على جهازك.**
- **`sh tools/xpix_agent/start_mac.sh`**: يشغّل السيرفر (التوكن بيتولّد مرة في `~/.xpix_agent_token` بصلاحيات 600؛ حطه في credentials بتاعة n8n ومتبعتوش في الشات).
- **`tools/xpix_agent/com.xpix.agent.plist.example`**: تشغيل تلقائي عند الدخول (اختياري).
- **`tools/xpix_agent/n8n_workflow_example.json`**: مسودة workflow (دهب 15 دقيقة → لقطة → تحميل الـ PNG). **ما اتجربتش في n8n حقيقي**؛ استورده وضيف عقدة Telegram Send Photo لشات الـ ID بتاعك بس.
- فيه كمان بوت تليجرام جاهز من فريق الماك (`scripts/xpix_bot.py`، PR #202): بيرد على شات المالك بس، قراءة وعرض ورسم بس. تقدر تستخدمه بدل n8n أو جنبه.
