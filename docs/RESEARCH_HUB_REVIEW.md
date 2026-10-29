# مراجعة الـ Research Hub: الصور × التابات × الفجوات (2026-10-29)

حالة المراجعة: الصور اتجردت من المحادثة (13 صورة)، والتابات اتفتحت وصُوّرت فعليًا في متصفح معاينة بالـ dark theme (عرض 800px)، مش على `main.py` الكامل ولا Python 3.11.

## 1) جرد الصور
كلها من حساب Threads واحد، بإعلانات "DM me / link in bio". **ما اتاخدش رقم ولا إشارة**، بس أفكار عرض وآليات.

| المصدر (الصور) | الأفكار فيه | اتغطى فين | اللي لسه ناقص |
|---|---|---|---|
| Polymarket/MiroFish "gobblewobble" (1، 2) | شريط دورة التنفيذ Scan→Settle بزمن كل مرحلة، رسم swarm للإجماع، order book، سجل صفقات، "profit pace" | Decision Trail (المراحل جدول، من غير زمن)، Consensus Map (رسم دائري للكاشفات) | شريط المراحل البصري، درجة إجماع واحدة. "profit pace" و"win streak" مرفوضين: مقاييس تسويق |
| Veles Quant Desk (3، 4) | قمع قتل الأفكار (86.7% kill)، خريطة عائلات الاستراتيجيات، "who pays us" (bps لكل عائلة)، plateau surface، markout decay، robustness matrix، سلّم أوامر مثبّت | Plateau Lab (سطح + walk-forward)، صفحة Veles القديمة (مصفوفة + markout) | **Kill Funnel، order ladder، "who pays us"، خريطة العائلات** |
| Grok Bot Trade Anatomy (5) | أدوار Analyst/Risk/Chief/Executor، order ticket، فحوصات قبل الأمر، جدول win-rate اللازم لكل R:R | Decision Trail (بوابات الإشارة) | order ticket، جدول break-even win rate لكل R:R (حسبة بسيطة وصادقة) |
| VANG-ALPHA خمس وكلاء (6) | Scout/Intelligence/Risk/Execution/Learning + audit trail | Decision Trail + `docs/AI_ROLES.md` | تسجيل قرارات AI نفسها (مين اقترح وإيه اتعرض) |
| JEV Engineering (7، 9، 10) | داشبورد نظام هندسي (swarm، throughput) | — | **مرفوض**: مش تداول |
| Claude×Quant (8، 9) | robustness 7×3 TF، Monte Carlo 7164 مسار، Quincunx | صفحتا Monte Carlo وVeles القديمتين | ربطهم بالـ Hub (لسه في الـ sidebar لوحدهم) |
| Polymarket bot 98eur (11) | resolution grid، inventory plane، side chain | Micro · Foundations القديمة | — |
| IV surface (12) | سطح تذبذب ضمني، spreads بحد خسارة | — | **مفيش**. مصدر مجاني: Deribit (كريبتو)، وفي المشروع `cboe_options.py`/`options_desk.py` |

## 2) مراجعة التابات
| التاب | شغال على | نقطة قوة | عيب/حد |
|---|---|---|---|
| Truth Court | lab حقيقي | بقى بيجمع تجارب كل التابات (649 دلوقتي بدل 564) | كل خلية سطح في Plateau بتتحسب تجربة مستقلة وهي مش مستقلة: الحد محافظ زيادة |
| Plateau Lab | شموع OKX حقيقية | ضد overfitting فعلًا (هضبة ≠ قمة) | المسبار MA cross بس، 1h/1d بس، مش بيجرب قواعد الـ lab الحقيقية |
| Regime Radar | شموع + Hyperliquid | funding/OI، ترابط الرموز | **ولا تاب بيقرا نظامه**، فلتر Thin ناقص، مفيش رسم زمني للأنظمة |
| Decision Trail | **mock** | سلامة الزمن، UNPROVEN | مفيش سجل إشارات حقيقي |
| Decay Watch | **mock** | قواعد ثابتة + سجل تحديات | نفس السبب |
| Consensus Map | lab حقيقي | بيكشف الصوت المكرر | ثابت من ملف الـ lab، ومرتبط بالأسماء بس |
| Command Center (جديد) | snapshots | بطاقة لكل تاب + مخطط تدفق | مفيش روابط لصفحات Veles/Monte Carlo/Micro |

## 3) التكامل
تم في هذه الجولة: (أ) Truth Court بيقرا `n_trials` من Plateau/Regime/Decay/Consensus. (ب) Command Center بيقرا الـ snapshots فقط (عدم استيراد كود التابات اتأكد باختبار). (ج) Decay بيستخدم N الكلي في Bonferroni بتاع المتحدّين.
لسه: Regime Radar مرسوم متقطّع في المخطط لأن حد مش بيقراه.

## 4) العرض البصري
تم: كل التابات على `ui_kit` بتاع التطبيق (كروت، حلقات، panels) وبتتبع قائمة الثيم عن طريق `hub_ui.set_theme(_kit_theme())`، ولكل تاب لون ورمز، ومسطرة t (Truth)، ورسم دائري للكاشفات (Consensus)، ومخطط تدفق. اتصلّح: تراكب أرقام مسطرة t، وكارت Consensus اللي كان بيلف.
لسه: حالة "قبل التشغيل" في Plateau وRegime عبارة عن جدول بس، مفيش رسم زمني لأنظمة السوق، العرض ما اتجرّبش على الموبايل ولا على ثيمات غير الـ dark، والشريط العلوي للتابات لونه أحمر موحّد (Streamlit) مش لون التاب.

## 5) اللي ناقص، بالأولوية
1. **سجل إشارات حقيقي** (التابين mock). السبب المرجح: الـ cron بيفلتر 4 نجوم. قرار المالك (`TG_MIN_STARS`).
2. ~~Kill Funnel~~ **اتبنى** (تاب 7). ~~جدول break-even win rate~~ **اتبنى** جواه. لسه order ticket في Trail.
2b. **إعادة تشغيل Strategy lab** (بإذن المالك): 611 صف من المدارس المنفردة (SMC/Elliott/Levels...) من غير t-stat، فمفيش حد حكم عليهم.
4. ~~تقطيع النتايج بنظام Regime~~ **اتبنى في Plateau Lab** (Regime Radar بقى مقروء). لسه Truth/Trail مش بيقطّعوا بالنظام.
5. رسم زمني للأنظمة + فلتر Thin.
6. روابط من Command Center لصفحات Veles/Monte Carlo/Micro.
7. سطح تذبذب ضمني (Deribit للكريبتو): بعد ما الباقي يثبت.
8. تشغيل `main.py` كامل على Python 3.11 ومراجعة الصفحة على موبايل وثيمات تانية.
