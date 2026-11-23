# Research task (web search), output one Markdown file. Be fru

- المصدر: `subagents`
- معرف الجلسة: `d72c5c58-ff10-455f-b893-3cef6d2bb5f1`
- البداية: 2026-11-23T07:56:42.487Z — النهاية: 2026-11-23T07:59:43.245Z
- الرسائل: مستخدم 32 · مساعد 30 · أدوات 30
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** Research task (web search), output one Markdown file. Be frugal: about 15 to 25 searches, no long quotes (max one short quote per source, under 15 words), cite URLs.

Context: we build "T.O X", a free browser-based engineering workspace that aims to cover the daily workflows of AutoCAD, Revit, Civil 3D, Primavera P6, Navisworks, AutoCAD Plant 3D, Revit MEP/HVAC tools, ArcGIS/QGIS, SketchUp/Coohom, quantity take-off tools (CostX/Planswift-like) and reality capture (ReCap/Pix4D/ODM), with an AI ag
- **طلبات المستخدم (أول 15):**
  1. Research task (web search), output one Markdown file. Be frugal: about 15 to 25 searches, no long quotes (max one short quote per source, under 15 wor
  2. <system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full repo
- **آخر رد للمساعد:** —

---

## المحادثة الكاملة

### user · 2026-11-23T07:56:42.487Z

Research task (web search), output one Markdown file. Be frugal: about 15 to 25 searches, no long quotes (max one short quote per source, under 15 words), cite URLs.

Context: we build "T.O X", a free browser-based engineering workspace that aims to cover the daily workflows of AutoCAD, Revit, Civil 3D, Primavera P6, Navisworks, AutoCAD Plant 3D, Revit MEP/HVAC tools, ArcGIS/QGIS, SketchUp/Coohom, quantity take-off tools (CostX/Planswift-like) and reality capture (ReCap/Pix4D/ODM), with an AI agent (voice + chat) that can run the tools. We want to know where users are unhappy with the existing products, so we can compete honestly by serving those needs.

Find, for each product family above, what users and reviewers currently complain about and ask for (2024 to 2026): pricing and licensing (subscriptions, named users, tokens/Flex), performance and file size, file format lock-in and interoperability (DWG/RVT/IFC/XER/LandXML), learning curve, collaboration, cloud/web versions and their limits, Mac/Linux support, automation and scripting gaps, and what they say about AI features (Autodesk Assistant/AI, Revit AI plugins, Primavera Cloud, ChatGPT/Claude use in AEC). Use sources like Autodesk forums and Ideas boards, Reddit (r/Revit, r/AutoCAD, r/civil3d, r/projectmanagement, r/gis, r/bim), G2/Capterra review summaries, the 2020 open letter from architecture firms to Autodesk and its follow-ups, buildingSMART/IFC discussions, and AEC tech press (AEC Magazine etc.). Also list notable AI-native or browser-native challengers (e.g. Snaptrude, Arcol, Qonic, Motif, Hypar, Speckle, Rayon, That Open Company) with one line each on what they do well.

Write the result to `/Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md` (create the folder if needed; do not touch any other file, do not run git). Structure: (1) top 10 cross-cutting pain points ranked by how often they appear, each with evidence links; (2) one short section per product family: top complaints, most requested features, the single workflow users most want to be faster; (3) AI: what users want from AI in these tools vs what vendors ship; (4) challengers table; (5) "Opportunities for T.O X": 10 to 15 concrete, buildable ideas, each tied to a pain point above, marked small/medium/large effort; (6) a short "not verified / weak evidence" list. Mark anything you could not confirm from a source as unverified; never invent numbers or prices. English, plain, concise (about 1500 to 2500 words).

Reply to me with: the file path, the 5 strongest opportunities in one line each, and what you could not verify.

### user · 2026-11-23T07:56:42.922Z

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered. Do not also send the report with SendMessage: your caller would get it twice.
</system-reminder>

### assistant · 2026-11-23T07:56:45.385Z

**أداة:** `ToolSearch`

```json
{
 "query": "select:WebSearch,WebFetch",
 "max_results": 2
}
```

### user · 2026-11-23T07:56:45.500Z

**نتيجة أداة:**
```

```

### assistant · 2026-11-23T07:56:47.770Z

**أداة:** `WebSearch`

```json
{
 "query": "open letter architecture firms Autodesk Revit cost development 2020 follow-up 2024 2025 AEC Magazine",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:56:48.779Z

**أداة:** `WebSearch`

```json
{
 "query": "Autodesk named user subscription Flex tokens complaints price increase 2025 multi-user license removed transacting directly",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:56:49.673Z

**أداة:** `WebSearch`

```json
{
 "query": "Revit users complaints slow large models single-threaded no backward compatibility file version 2025 forum",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:56:50.368Z

**أداة:** `WebSearch`

```json
{
 "query": "Civil 3D complaints slow crashes corridors surfaces data shortcuts users frustrated 2025",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:56:51.252Z

**أداة:** `WebSearch`

```json
{
 "query": "Primavera P6 user complaints outdated interface expensive Primavera Cloud OPC limitations reviews 2025",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:56:51.939Z

**أداة:** `WebSearch`

```json
{
 "query": "AutoCAD Web app limitations AutoCAD for Mac missing features LISP complaints reviews 2025",
 "mode": "standard"
}
```

### user · 2026-11-23T07:56:58.256Z

<details><summary>نتيجة أداة (4572 حرف)</summary>

```
Web search results for query: "open letter architecture firms Autodesk Revit cost development 2020 follow-up 2024 2025 AEC Magazine"

Links: [{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=6352"},{"title":"Architects Versus Autodesk","url":"https://www.architectmagazine.com/?p=350678"},{"title":"Architects Versus Autodesk","url":"https://www.architectmagazine.com/technology/architects-versus-autodesk_o"},{"title":"22 minute read","url":"https://issuu.com/x3dmedia/docs/aec_q3_2022/s/16813805"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=6327"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/wp-json/wp/v2/views/6352"},{"title":"letter to Autodesk","url":"https://aecmag.com/bim/letter-to-autodesk-aec-customers-demand-better-value/"},{"title":"letter to Autodesk","url":"https://aecmag.com/bim/letter-to-autodesk-aec-customers-demand-better-value/}}"},{"title":"Autodesk Open Letter","url":"https://aecmag.com/bim/a-tale-of-two-open-letters/"},{"title":"letter to Autodesk","url":"https://aecmag.com/bim/autodesk-aec-customers-demand-better-value/"},{"title":"32 minute read","url":"https://issuu.com/x3dmedia/docs/aec_julyaugust20/s/11386785"},{"title":"49825 autodesk admits its underinvested in revit development over 100 firms want change","url":"https://www.enr.com/articles/49825-autodesk-admits-its-underinvested-in-revit-development-over-100-firms-want-change"},{"title":"www.archpaper.com","url":"https://www.archpaper.com/?p=285666"},{"title":"zha grimshaw and other large firms pen open letter decrying issues with revit","url":"https://archinect.com/news/article/150208994/zha-grimshaw-and-other-large-firms-pen-open-letter-decrying-issues-with-revit"},{"title":"autodesk responds to open letter on revit","url":"https://architosh.com/2020/08/autodesk-responds-to-open-letter-on-revit/"},{"title":"The Open Letter to Autodesk: two years on","url":"https://aecmag.com/opinion/the-open-letter-two-years-on/"},{"title":"autodesk we have underinvested in architectural modeling functionality in recent years and are working to make that right","url":"https://archinect.com:443/news/article/150209841/autodesk-we-have-underinvested-in-architectural-modeling-functionality-in-recent-years-and-are-working-to-make-that-right"},{"title":"www.archpaper.com","url":"https://www.archpaper.com/?p=285769"},{"title":"11 minute read","url":"https://issuu.com/x3dmedia/docs/aec_q3_2022/s/16813804"}]

The search turned up coverage of the 2020 letter and its follow-ups, but nothing clearly dated 2024 or 2025, so the later history is thin.

- **The 2020 letter:** AEC Magazine published it, and it was signed by 17 firms at first, including Grimshaw and Zaha Hadid Architects. The original group of 17 firms (now 35 firms), co-ordinated by industry veteran and IT consultant Iain Godwin, created the open letter as price increases of Autodesk's flagship BIM tool, Revit, had dramatically increased the cost of ownership.
- **Autodesk's response:** Autodesk replied point by point. Its CEO-level response said it had significantly increased its engineering investment in Revit Architecture at the beginning of that year. Autodesk also argued that software prices were not a major driver of firm costs, since it compared the 2019 revenues of the 17 signatories with their Autodesk spending.
- **Second year-on-year check (2022):** AEC Magazine's "two years on" piece reported that the Open Letter Group saw some change. The Revit team started hiring programmers, and recent releases enhanced or added features that had been outstanding for years. Still, the updates delivered had not been deep or consequential, according to the group's statement.
- **Second letter:** A later letter from Nordic architectural associations is covered in AEC Magazine's "A tale of two (open) letters." That piece says it is not a repeat letter but a statement that little has changed. The article has no clear date in the results, so I can't confirm whether it is from 2023, 2024, or 2025.
- **Autodesk's later admission:** Autodesk later acknowledged underinvestment in architectural modeling. ENR reported that the number of architecture firms requesting more Revit development had grown to 116 by August 20. That article's year is not shown in the results.

For 2024–2025 developments, such as any new Autodesk pricing changes or a further follow-up letter, a more targeted search would be needed.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:56:58.505Z

<details><summary>نتيجة أداة (4510 حرف)</summary>

```
Web search results for query: "Autodesk named user subscription Flex tokens complaints price increase 2025 multi-user license removed transacting directly"

Links: [{"title":"Unannounced license fee increase","url":"https://forums.autodesk.com/t5/installation-licensing-forum/unannounced-license-fee-increase/td-p/13771637"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/in/campaigns/transition-to-named-user.html"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/ca-en/campaigns/transition-to-named-user"},{"title":"Understand Autodesk subscriptions and licenses","url":"https://www.autodesk.com/learn/ondemand/course/be-more-efficient-as-an-autodesk-account-administrator/unit/2quOKZyxGtJfV9PsneTr9l"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/za/campaigns/transition-to-named-user"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/eu/campaigns/transition-to-named-user"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/uk/campaigns/transition-to-named-user"},{"title":"Key Learnings","url":"https://autodesk.com/autodesk-university/class/Why-You-Need-Both-Flex-and-Subscription-2024"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/asean/campaigns/transition-to-named-user"},{"title":"Autodesk, your way","url":"https://www.autodesk.com/in/campaigns/transition-to-named-user"},{"title":"Negotiation Services Benchmarking Vera AI Case Studies Videos About Free benchmark Contact Us","url":"https://redresscompliance.com/autodesk-perpetual-to-subscription-cost-analysis"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/wp-json/wp/v2/news/57543"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/hi/tags/subscription"},{"title":"Hi Everyone,","url":"https://forums.autodesk.com/t5/subscription-changes/introducing-flex-a-new-pay-as-you-go-option-for-customers/td-p/10549204"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=57605"},{"title":"COMMITTED TO LISTENING, INVESTING, AND DELIVERING","url":"https://www.autodesk.com/customer-value.html"},{"title":"& Construction","url":"https://autodesk.com/customer-value/technology-admin/enhancements-2024"}]

The search didn't turn up anything on the multi-user license being removed or on transacting directly, and no clear report of a 2025 Flex-specific price backlash. The results do cover a 2025 price increase, the Flex model, and some reseller guidance.

- **Price increase:** A forum user reported an unannounced 20% license fee rise. Another forum member replied that Autodesk had announced an increase in late 2024 that took effect January 7, 2025, and that it was covered by most "cad" media online and an email blast from Autodesk to account admins. The complainant said there was no official communication apart from the invoice. These are anecdotes from one forum thread, not confirmed reporting on the scale of the increase.
- **How Flex works:** Autodesk says users are charged a daily rate per product once every 24 hours, and if your team does not have enough tokens, users will lose access to Flex and will be unable to open the product.
- **Named-user vs. Flex:** Autodesk's own training material says a subscription is dedicated to one named user. Admins can reassign access to other users, but only one person at a time can use that subscription. By contrast, Flex is a shared pool of tokens that supports any number of named users.
- **Pricing terms:** Autodesk's pages say all Autodesk pricing is subject to change without notice. For multi-year terms, you'll secure your price for three years.
- **Flex minimum:** In 2025, Autodesk lowered the Flex entry point, with a new lower minimum of 33 tokens for $99, down from 100 tokens for $300, starting June 4.
- **Reseller analysis:** A consultancy's August 2026 advisory (Redress Compliance, based on 2024–2025 estate reviews) says roughly a third of seats price better on Flex than on a subscription, and that the standard reseller advice is to convert every former perpetual and network seat into a named user subscription for continuity. This is one vendor-side source with its own commercial interest.

Gaps: I found nothing confirming that a multi-user license was removed or that Autodesk stopped selling direct. Those claims would need Autodesk's partner or licensing announcements, which this search didn't reach.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:56:58.581Z

<details><summary>نتيجة أداة (4653 حرف)</summary>

```
Web search results for query: "Revit users complaints slow large models single-threaded no backward compatibility file version 2025 forum"

Links: [{"title":"Revit is very slow, but CPU is only at 30%","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-is-very-slow-but-cpu-is-only-at-30/m-p/7057417"},{"title":"Revit is very slow, but CPU is only at 30%","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-is-very-slow-but-cpu-is-only-at-30/m-p/7046609"},{"title":"Revit is very slow, but CPU is only at 30%","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-is-very-slow-but-cpu-is-only-at-30/m-p/7059158"},{"title":"Improving Revit Model Health and Performance: Find What’s Slowing You Down","url":"https://www.autodesk.com/blogs/aec/2026/11/13/improving-revit-model-health-and-performance/"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/multi-thread/idi-p/8260315/page/2"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-architecture-forum/very-slow-speed-revit-2017/td-p/6795972"},{"title":"Revit slow performance","url":"https://autodesk.com/fr/support/technical/article/Revit-Slow-Performance"},{"title":"# Multi-Core Support?","url":"https://forums.sketchup.com/t/multi-core-support/54440.md"},{"title":"Revit Architecture Forum","url":"https://forums.autodesk.com/t5/revit-architecture-forum/very-slow-speed-revit-2017/m-p/6798547/highlight/true"},{"title":"Revit Architecture Forum","url":"https://forums.autodesk.com/t5/revit-architecture-forum/very-slow-speed-revit-2017/m-p/6800527/highlight/true"},{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/revit-slowdown/td-p/3562790"},{"title":"CPU cores and Toposolid nodes","url":"https://forums.autodesk.com/t5/revit-architecture-forum/cpu-cores-and-toposolid-nodes/m-p/12441556"},{"title":"REVIT 2024 SLOW","url":"https://forums.autodesk.com/t5/revit-structure-forum/revit-2024-slow/td-p/12517919"},{"title":"REVIT 2024 SLOW","url":"https://forums.autodesk.com/t5/revit-structure-forum/revit-2024-slow/m-p/12539851"},{"title":"Hi everyone,","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-lagging/m-p/9891227"},{"title":"slow Revit model","url":"https://forums.autodesk.com/t5/revit-architecture-forum/slow-revit-model/m-p/11667008"},{"title":"Best Practices for model maintenance in Revit","url":"https://autodesk.com/support/technical/article/Revit-file-maintenance-best-practices"},{"title":"Extremely slow performance","url":"https://forums.autodesk.com/t5/revit-architecture-forum/extremely-slow-performance/td-p/12682189"}]

The search turned up plenty of forum complaints about slow large Revit models, but little on backward compatibility and nothing that is clearly about 2025 specifically.

**Single-threading and CPU use:** Forum users often say Revit leans on one core. One user notes that you most likely see a single core (single thread) doing all the work on many Revit tasks. A reply disputes the claim, saying Revit is multi-threaded in many aspects, with rendering as one example. A 2026 user says they (allegedly) improve use of multi-cores with each version. Complaints that the architecture is outdated also appear, such as the claim that Revit is built on old software architecture and does not support multi-threaded tasks natively. That is one user's opinion, not a verified technical finding.

**Large-file slowness:** Users report long waits on big files. One describes moving a wall several cm's it takes about 2-3 min. Another notes that a staggering amount of warning can bog the project down. A thread argues that the convenience of having one file will wear off as it gets larger and larger, and suggests splitting models into smaller linked files.

**Version complaints:** A Revit 2024 thread is frustrated that 2020 CRAZY SLOW, 2021 VERY SLOW, and says the issue persists in 2024. Autodesk's own blog says model performance depends on much more than file size, citing linked models, sync activity, local caches, and hardware.

**Gaps:** None of the results address backward compatibility or file-version issues directly, so that part of your query is unsupported here. Autodesk's support page lists storage media and the operating system (OS updates can influence Revit performance) as common causes, and recommends testing links and add-ons. A follow-up search on Autodesk's Revit 2025 release notes or forums about file version upgrades would help fill the backward-compatibility gap.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:56:58.671Z

<details><summary>نتيجة أداة (4331 حرف)</summary>

```
Web search results for query: "Primavera P6 user complaints outdated interface expensive Primavera Cloud OPC limitations reviews 2025"

Links: [{"title":"Listing Thumbnail","url":"https://aws.amazon.com/marketplace/pp/prodview-4fxcbhan3x2zq"},{"title":"Listing Thumbnail","url":"https://aws.amazon.com/marketplace/pp/B08YD8XXBV"},{"title":"# Oracle Primavera Cloud Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/145503/Oracle-Primavera/reviews/"},{"title":"www.spotsaas.com","url":"https://www.spotsaas.com/product/oracle-primavera/reviews?page=21"},{"title":"# Oracle Primavera Cloud Software Pricing, Alternatives & More 2026 | Capterra","url":"https://www.capterra.com/p/181380/Oracle-Primavera/"},{"title":"primavera p6 enterprise project portfolio management","url":"https://www.gartner.com/reviews/product/primavera-p6-enterprise-project-portfolio-management"},{"title":"www.g2.com","url":"https://www.g2.com/products/oracle-primavera-unifier-project-controls/reviews"},{"title":"reviews and filters","url":"https://g2.com/products/oracle-primavera/reviews_and_filters?page=3"},{"title":"reviews and filters","url":"https://g2.com/products/oracle-primavera/reviews_and_filters?page=4"},{"title":"Oracle Primavera","url":"https://www.capterra.com/p/145503/Oracle-Primavera/"},{"title":"1 million+ businesses helped. Get advice","url":"https://www.softwareadvice.com/construction/primaverp6eppm-profile/"},{"title":"www.softwareadvice.com.au","url":"https://www.softwareadvice.com.au/software/151381/primaverp6eppm"},{"title":"oracle primavera","url":"https://www.capterra.co.uk/reviews/181380/oracle-primavera"},{"title":"Capterra   3201750","url":"https://www.capterra.com/p/145503/Oracle-Primavera/reviews/Capterra___3201750/"},{"title":"www.spotsaas.com","url":"https://www.spotsaas.com/product/oracle-primavera/reviews?page=20"},{"title":"primavera p6","url":"https://www.selecthub.com/p/ppm-software/primavera-p6/"},{"title":"# Primavera Unifier Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/181519/Oracle-Primavera-Unifier/reviews/"},{"title":"www.saasworthy.com","url":"https://www.saasworthy.com/product/oracle-primavera/reviews"}]

The search turned up user feedback on P6's interface, cost, and learning curve, but little specific to Primavera Cloud (OPC) limitations or 2025 reviews.

- **Interface:** Reviewers call the look dated. One G2 user says P6's graphical reports look outdated next to current tools, so people export raw data to spreadsheets to build S-curves and histograms (Graphical reports generated directly from Primavera P6 look outdated compared to some current offerings in the market). SelectHub reports that over 83% of users reported that it is not intuitive and friendly for a novice and requires training to use the program. Other users describe the main screen as needing more visual polish (The main interface could be more interactive with light colors.).
- **Cost and learning curve:** SelectHub lists Expensive and Steep learning curve as cons, and says Primavera P6 pricing starts at $3,168 (Per User, Annually). SaaSworthy's AI summary of user reviews also flags high cost, steep learning curve, limited customization, and an outdated interface (High Cost, Steep Learning Curve, Limited Customization Options, Outdated User Interface).
- **Positives:** Many reviewers still rate it well for scheduling depth. One G2 reviewer describes the interface as easy enough that anyone can learn within 2-3 days. SelectHub reports an 84% recommendation rate across 371 reviews.
- **Primavera Cloud:** Capterra's summary says Oracle Primavera Cloud offers a functional interface for detailed project control, but ease of use depends on experience level. Capterra lists a starting price of $100 per year, but I couldn't confirm whether that applies to the full product. Softwareadvice says pricing details for Oracle Primavera Cloud are not shared publicly.
- **Gaps:** I found no clear 2025 review set focused on OPC-specific limitations. Most results are aggregator pages with mixed dates, and some reviews are from 2023. Treat the cost figures as indicative, and check Oracle's current pricing directly.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:56:58.698Z

<details><summary>نتيجة أداة (4112 حرف)</summary>

```
Web search results for query: "AutoCAD Web app limitations AutoCAD for Mac missing features LISP complaints reviews 2025"

Links: [{"title":"LISP files","url":"https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/File-Management/AutoCAD_Web_Help_File_Management_Lisp_html.html"},{"title":"Getting Started","url":"https://autocad-vagon.pages.dev/blog/autocad-online-limitations-you-should-know/"},{"title":"What’s New in AutoCAD 2023? LISP API in AutoCAD Web App","url":"https://www.autodesk.com/blogs/autocad/whats-new-in-autocad-2023-lisp-api-in-autocad-web-app/"},{"title":"What's New in the AutoCAD Web App","url":"https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/AutoCAD_Web_Help_Whats_new_html.html"},{"title":"AutoCAD Web Migration Guide","url":"https://constructivision.github.io/ConstructiVision/legacy/developer-notes/autocad-web-migration.html"},{"title":"About Working With AutoCAD Drawings in AutoCAD LT","url":"https://help.autodesk.com/cloudhelp/2021/ENU/AutoCAD-LT/files/GUID-97C5344F-CF59-4B02-9EA2-22247820D239.htm"},{"title":"Frequently Asked Questions","url":"https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/AutoCAD_Web_Help_FAQs_html.html"},{"title":"Az AutoCAD Web legfontosabb szolgáltatásai","url":"https://www.autodesk.com/hu/products/autocad-mobile/features"},{"title":"Az AutoCAD Web legfontosabb szolgáltatásai","url":"https://www.autodesk.com/hu/products/autocad-web/features"},{"title":"Key features of AutoCAD Web","url":"https://www.autodesk.com/eu/products/autocad-web-app/features"},{"title":"lisp api","url":"https://www.autodesk.com/blogs/autocad/tag/lisp-api/"},{"title":"Objects Missing in Drawing","url":"https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/File-Management/AutoCAD_Web_Help_VISUALDIFFERENCES_html.html"},{"title":"AutoCAD Web의 주요 기능","url":"https://www.autodesk.com/kr/products/autocad-mobile/features"},{"title":"Commands and System Variables","url":"https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/AutoCAD_Web_Help_List_Commands_html.html"}]

I ran one search. It returned mostly Autodesk help pages and a few third-party posts, but nothing on AutoCAD for Mac or on 2025 user reviews, so those parts of your query are unanswered.

- **LISP on the web app:** Autodesk's help says not all desktop LISP/AutoLISP functionality, such as creating or modifying LISP routines, is available in the AutoCAD web app, and that not all of the commands and system variables in AutoCAD or AutoCAD LT are available. The web app only supports LSP (.lsp) files, and LISP is only available with an AutoCAD subscription.
- **Conflicting claim:** A migration guide from constructivision.github.io (index 5-1 to 5-2) says AutoLISP cannot run in AutoCAD Web, AutoCAD mobile apps, or any cloud-based Autodesk product. That contradicts Autodesk's own documentation, so I'd treat it as unreliable.
- **Missing features in general:** A third-party post from March 2026 says the browser version focuses almost entirely on 2D drafting and viewing, and that tools for creating or editing 3D models are not available. It is a secondary source, so weigh it accordingly.
- **Drawing fidelity:** Autodesk says that point clouds, underlays (such as PDF or DGN underlays), and certain images and other types of external references will not display in the web app. It also says proxy objects and custom objects, including objects from AutoCAD Mechanical, Electrical, Civil 3D, Map 3D, MEP, P&ID, and Plant 3D may appear differently, though the file data is unchanged.
- **Mac:** The only Mac reference is an older AutoCAD LT help page (2021) stating that AutoCAD for the Mac also has feature set limitations. It gives no specifics.
- **Sharing:** Autodesk notes that drawings that are shared with you are in view-only mode, and the editing tools are unavailable.

For 2025 reviews and current Mac feature gaps, a follow-up search on Autodesk's AutoCAD for Mac feature comparison and recent user forum threads would be needed.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:56:58.741Z

<details><summary>نتيجة أداة (4612 حرف)</summary>

```
Web search results for query: "Civil 3D complaints slow crashes corridors surfaces data shortcuts users frustrated 2025"

Links: [{"title":"Overcoming the Seven Deadly Sins of Civil 3D Project Performance 2026","url":"https://www.autodesk.com/autodesk-university/class/Overcoming-the-Seven-Deadly-Sins-of-Civil-3D-Project-Performance-2026"},{"title":"# Civil 3D Reviews","url":"https://www.g2.com/products/civil-3d"},{"title":"Poor Performance on 65km Road Design","url":"https://forums.autodesk.com/t5/civil-3d-forum/poor-performance-on-65km-road-design/m-p/9073603"},{"title":"why civil 3d is poor software aimed only at autodesk profits","url":"https://forums.autodesk.com/t5/civil-3d-forum/why-civil-3d-is-poor-software-aimed-only-at-autodesk-profits/td-p/12894406"},{"title":"# Civil 3D Reviews","url":"https://www.g2.com/products/civil-3d/reviews"},{"title":"autodesk.com","url":"https://forums.autodesk.com/t5/civil-3d-forum/poor-performance-on-65km-road-design/m-p/9057590"},{"title":"Top 10 Optimization Tips for Civil 3D","url":"https://resources.imaginit.com/support-blog/top-10-optimization-tips-for-civil-3d"},{"title":"Poor Performance on 65km Road Design","url":"https://forums.autodesk.com/t5/civil-3d-forum/poor-performance-on-65km-road-design/m-p/9059151"},{"title":"Poor Performance on 65km Road Design","url":"https://forums.autodesk.com/t5/civil-3d-forum/poor-performance-on-65km-road-design/td-p/9055453"},{"title":"Civil 3D Forum","url":"https://forums.autodesk.com/t5/civil-3d-forum/newer-features-slower-to-react-than-their-classic-counterparts/m-p/9293816"},{"title":"Civil 3D Forum","url":"https://forums.autodesk.com/t5/civil-3d-forum/when-is-autodesk-going-to-fix-all-the-bugs/m-p/10380743"},{"title":"autodesk.com","url":"https://forums.autodesk.com/t5/civil-3d-forum/identifying-the-reasons-for-poor-performance-and-what-are-the/m-p/10680340"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/civil-3d-forum/civil-3d-2025-1-release-is-live/td-p/12968870"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/199886/Civil-3D/reviews"},{"title":"What’s New in Civil 3D 2025.1","url":"https://www.autodesk.com/blogs/aec/2024/08/19/whats-new-in-civil-3d-2025-1/"},{"title":"civil 3d slow performance in large data sets","url":"https://resources.imaginit.com/civil-3d/civil-3d-slow-performance-in-large-data-sets"}]

Recent complaints about Civil 3D slowness and crashes are consistent across user reviews, forums, and reseller tips, though most of the evidence is anecdotal.

**User complaints**
- G2 reviewers describe crashes and data loss when handling multiple files, along with slowdowns on large or complex projects, especially on lower-powered machines (users report data loss due to crashes and unsaved files). One reviewer said the software can't properly handle larger models, and it crashes a lot.
- An Autodesk Forum thread on a 65 km road design, built with data shortcuts, describes very slow alignment adjustments while the poster was finding grades (the process was really slow as I was adjusting alignment to find right grades for the design.). A forum responder advised prudent data management... using xrefs and shortcuts as well as breaking the design up into manageable lengths.
- Another user reported that a long session slows down especially if the corridors are big and you extract solids from it.

**Technical explanations from third parties**
- An Autodesk University 2026 class frames slowdowns as a result of structural decisions in file setup and data management, and says surface building, corridors, and data shortcuts create cascading performance problems.
- Imagine IT's optimization guidance notes that too many breaklines = slow surface rebuilds and recommends splitting large surfaces and imagery into separate master files that are attached via external references and data shortcuts.

**Vendor response**
- Autodesk's 2025.1 release notes claim performance enhancements for corridors and surfaces speed up data processing to reduce wait time between tasks. Autodesk's own figures for corridor grip editing with object snap are vendor claims, not independent benchmarks. One forum user said 2025 works faster and better but with some things I revert to 2024.

**Caveats:** Most of the complaint evidence comes from a small number of G2 reviews (each theme cites only two) and forum threads, some from 2021 and earlier. I found no systematic 2025 benchmark study, so the picture is directional rather than measured.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-23T07:57:00.997Z

**أداة:** `WebSearch`

```json
{
 "query": "Autodesk Assistant Revit AI 2025 2026 users reaction AEC Magazine \"Autodesk AI\" neural CAD skepticism",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:02.141Z

**أداة:** `WebSearch`

```json
{
 "query": "Nordic architects open letter Autodesk 2023 data ownership cloud lock-in Forma \"Future AEC Software Specification\" AEC Magazine",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:02.989Z

**أداة:** `WebSearch`

```json
{
 "query": "IFC export Revit problems data loss interoperability complaints buildingSMART forum IFC5 2025",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:03.729Z

**أداة:** `WebSearch`

```json
{
 "query": "ArcGIS Pro credits licensing cost complaints switch to QGIS users 2025 QGIS pain points",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:04.569Z

**أداة:** `WebSearch`

```json
{
 "query": "Navisworks complaints outdated clash detection false positives alternatives Revizto Solibri 2025",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:05.360Z

**أداة:** `WebSearch`

```json
{
 "query": "SketchUp subscription price complaints SketchUp for Web limitations Free plan removed features 2025 users",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:06.199Z

**أداة:** `WebSearch`

```json
{
 "query": "PlanSwift CostX Bluebeam takeoff software complaints Windows only expensive learning curve AI takeoff 2025 reviews",
 "mode": "standard"
}
```

### user · 2026-11-23T07:57:11.604Z

<details><summary>نتيجة أداة (4132 حرف)</summary>

```
Web search results for query: "Autodesk Assistant Revit AI 2025 2026 users reaction AEC Magazine "Autodesk AI" neural CAD skepticism"

Links: [{"title":"autodesk assistant in revit tech preview","url":"https://www.autodesk.com/blogs/aec/2026/04/22/autodesk-assistant-in-revit-tech-preview/"},{"title":"• Autodesk Assistant in Revit – Tech Preview: Your AI Support to Create More and Work Smarter","url":"https://www.autodesk.com/blogs/aec/author/minjiewang/"},{"title":"Autodesk Assistant (Tech Preview)","url":"https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-68D8FE6D-C5B0-4503-AE27-02C715BAC25B.htm"},{"title":"Shaping the Future of Your Agentic AI Partner","url":"https://www.autodesk.com/blogs/aec/2025/12/08/shaping-the-future-of-your-agentic-ai-partner/"},{"title":"Youve Heard About Autodesk Assistant in Revit Now Heres How to Actually Use It 2026","url":"https://www.autodesk.com/autodesk-university/class/Youve-Heard-About-Autodesk-Assistant-in-Revit-Now-Heres-How-to-Actually-Use-It-2026"},{"title":"Autodesk Assistant (Tech Preview) Enhancements","url":"https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-51526618-271B-4331-B9E6-FB1D9FC14FBD.htm"},{"title":"Autodesk’s most ambitious AI play yet","url":"https://aecmag.com/ai/autodesks-most-ambitious-ai-play-yet/"},{"title":"“Can you query that 500 Pantin housing model?”","url":"https://fi.linkedin.com/in/helenawahlstrom"},{"title":"Autodesk AI 搭載","url":"https://www.autodesk.com/jp/solutions/autodesk-ai/autodesk-assistant"},{"title":"martin robles bim","url":"https://mx.linkedin.com/in/martin-robles-bim"},{"title":"Powered by Autodesk AI","url":"https://www.autodesk.com/solutions/autodesk-ai/autodesk-assistant"},{"title":"Autodesk AI로 구현","url":"https://www.autodesk.com/kr/solutions/autodesk-ai/autodesk-assistant"},{"title":"Autodesk AI","url":"https://www.autodesk.com/solutions/ai-in-architecture-engineering"},{"title":"AU 2025: Top Autodesk Construction Announcements","url":"https://www.autodesk.com/blogs/construction/?p=20390"},{"title":"AI-Powered Design and Make Updates for AECO","url":"https://www.autodesk.com/blogs/aec/2024/10/11/ai-powered-design-and-make-updates-for-aeco/"},{"title":"AI in Architecture and Engineering","url":"https://www.autodesk.com/solutions/autodesk-ai/ai-in-architecture-engineering"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=54116"},{"title":"Powered by Autodesk AI","url":"https://www.autodesk.com/solutions/autodesk-assistant"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=56350"}]

The search turned up Autodesk's own material and a few individual reactions, but no survey or broad review of user sentiment, and nothing that addresses the "neural CAD" skepticism angle directly.

- **Autodesk's positioning:** Autodesk describes Assistant in Revit as a tech preview and frames it as the next step in its AI work. It is a conversational, generative AI experience that works within the tools people use every day.
- **Safeguards:** The Revit help pages say Assistant actions are logged in the Revit journal, and AI-driven changes are labeled in the Undo menu. Autodesk's general product page adds that users should review outputs and apply professional judgment.
- **AEC Magazine coverage:** An AEC Magazine article on Autodesk's broader AI strategy describes a standalone Assistant that would act as an orchestrator across Autodesk's products. It also notes that the core users would likely range from experienced operators to laypeople. I didn't see reader reaction or critical commentary in the excerpt.
- **Practitioner reaction:** One BIM professional's post after testing the Revit 2027 assistant was enthusiastic, calling it cool, fun, and exciting. That is one person's view, not a broad sample.

Gaps: I didn't find the AEC Magazine coverage of Revit Assistant reaction itself, or any published skepticism about it. A follow-up search on AEC Magazine or Revit user forums would be needed for that.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:11.735Z

<details><summary>نتيجة أداة (4253 حرف)</summary>

```
Web search results for query: "SketchUp subscription price complaints SketchUp for Web limitations Free plan removed features 2025 users"

Links: [{"title":"# New Pricing Issue","url":"https://forums.sketchup.com/t/new-pricing-issue/335574.md"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/211798/SketchUp/pricing/"},{"title":"# Open Letter: Time to say goodbye to Sketchup as an enthusiastic non-professional because of the pricing model","url":"https://forums.sketchup.com/t/open-letter-time-to-say-goodbye-to-sketchup-as-an-enthusiastic-non-professional-because-of-the-pricing-model/183816.md?page=2"},{"title":"Price increases – another increase every year? 😵","url":"https://forums.sketchup.com/t/price-increases-another-increase-every-year/329950?page=2"},{"title":"Price increases – another increase every year? 😵","url":"https://forums.sketchup.com/t/price-increases-another-increase-every-year/329950?page=3"},{"title":"Taking a break from SketchUp","url":"https://forums.sketchup.com/t/taking-a-break-from-sketchup/348720?page=2"},{"title":"New Pricing Issue","url":"https://forums.sketchup.com/t/new-pricing-issue/335574"},{"title":"SketchUp Pricing 2026: Go, Pro, Studio & iPad Plans Compared","url":"https://www.myarchitectai.com/blog/sketchup-pricing"},{"title":"What has happened to sketchup?","url":"https://forums.sketchup.com/t/what-has-happened-to-sketchup/207310"},{"title":"WEB sketchup (FREE) version start limit download times?","url":"https://forums.sketchup.com/t/web-sketchup-free-version-start-limit-download-times/347759"},{"title":"SKETCHUP SUBSCRIPTION PRICE","url":"https://forums.sketchup.com/t/sketchup-subscription-price/320829"},{"title":"Open Letter: Time to say goodbye to Sketchup as an enthusiastic non-professional because of the pricing model","url":"https://forums.sketchup.com/t/open-letter-time-to-say-goodbye-to-sketchup-as-an-enthusiastic-non-professional-because-of-the-pricing-model/183816?page=3"},{"title":"SketchUp Pricing Overview","url":"https://www.g2.com/products/sketchup/pricing"},{"title":"Subscription Plans","url":"https://help.sketchup.com/admin/subscriptions"},{"title":"SketchUp Review 2026: Download, App, Sign In, Free Plan & FAQs","url":"https://nubiapage.com/sketchup-review-2026-download-app-sign-in-free-plan/"},{"title":"He said to me not to complain, and instead of do what eric is listing in his post…","url":"https://forums.sketchup.com/t/subscription/127406?page=3"}]

Here's what the search turned up. It's mostly forum posts and third-party pricing pages, so treat the details as indicative rather than official.

**Price increases:** Forum users reported that the annual Pro price rose from $349 to $399 in July 2025. One user said the month-to-month plan cost more than the annual plan, which they found puzzling (the annual price for Sketchup Pro would be increasing $50 from $349 to $399 on July 2nd). A third-party guide also cites the $349-to-$399 increase as something that had some users grumbling on the forums.

**Free web plan limits:** A forum user reported that the free web version limited download times(and create new project) to 2/month. A SketchUp staff reply acknowledged that some of you are currently seeing limits on new file creation and downloads on SketchUp for Web Free. Like all companies, we're constantly evaluating our offerings and pricing, including what we provide for free.

**Removed features:** A Capterra summary says the free version no longer supports extensions, limiting its capabilities. Other reviewers note that the shift to the web platform has reduced its usability, particularly when offline access is needed.

**Other complaints:** Users also point to the loss of perpetual licences and sign-in problems. One 2026 review says subscription pricing has risen while perpetual licences are gone entirely and lists frequent sign in and device authorisation problems as a drawback.

**Caveats:** Pricing sources disagree. One aggregator lists Go at $19.99 per user per month, and another gives the Go plan as roughly $129–139 per year. Verify current prices and plan contents on sketchup.com before relying on them.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:11.988Z

<details><summary>نتيجة أداة (3894 حرف)</summary>

```
Web search results for query: "Navisworks complaints outdated clash detection false positives alternatives Revizto Solibri 2025"

Links: [{"title":"navisworks vs revizto","url":"https://www.selecthub.com/building-information-modeling-software/navisworks-vs-revizto/"},{"title":"All blog posts","url":"https://revizto.com/en/clash-detection-navisworks-revizto/"},{"title":"www.selecthub.com","url":"https://www.selecthub.com/building-information-modeling-software/navisworks/alternatives/"},{"title":"Compare the Top Enterprise Clash Detection Software as of July 2026","url":"https://sourceforge.net/software/clash-detection/for-enterprise/"},{"title":"# Navisworks, Revizto vs Procore Comparison","url":"https://www.g2.com/compare/navisworks-vs-revizto-vs-procore"},{"title":"All blog posts","url":"https://revizto.com/resources/blog/revizto-vs-navisworks-vs-acc-clash-data-future-planning"},{"title":"Compare Navisworks and Revizto","url":"https://www.g2.com/compare/navisworks-vs-revizto"},{"title":"Compare the Top Clash Detection Software in Europe as of July 2026","url":"https://sourceforge.net/software/clash-detection/europe/"},{"title":"Compare the Top Clash Detection Software in the USA as of July 2026","url":"https://sourceforge.net/software/clash-detection/usa/"},{"title":"Compare the Top Clash Detection Software in the UK as of January 2026","url":"https://sourceforge.net/software/clash-detection/uk"},{"title":"Best Clash Detection Software for Navisworks","url":"https://slashdot.org/software/clash-detection/for-navisworks/"},{"title":"Best Clash Detection Software for Revizto","url":"https://slashdot.org/software/clash-detection/for-revizto/"},{"title":"# Compare Revizto vs Navisworks 2026 | Capterra","url":"https://www.capterra.com/compare/171336-233414/Revizto-vs-Navisworks"},{"title":"Best Clash Detection Software","url":"https://sourceforge.net/software/clash-detection"},{"title":"Average Ratings 0 Ratings","url":"https://slashdot.org/software/comparison/Navisworks-vs-Solibri-Office/"},{"title":"News December 04, 2020","url":"https://revizto.com/en/there-is-more-than-one-way-to-clash-check-a-model"}]

The search turned up mostly vendor marketing and comparison-site content, with little direct evidence on false positives or on Navisworks being outdated.

- **Navisworks' reputation:** One Revizto blog describes Navisworks as the industry standard for "hard" clash detection for decades. The same post says it often struggles with data longevity. Since Revizto sells a competing product, treat that as a vendor claim.
- **Solibri as an alternative:** A 2020 Revizto post says Solibri can do an incredibly advanced version of clash detection and also checks model data. It adds that Solibri only reads in IFC files whereas Navisworks lets you bring in native models from most authoring tools. Its basic clash rule is very similar to how Navisworks does clash detection.
- **Revizto:** Its clash detection is marketed as one of the most robust features of Revizto. A Revizto comparison was based on September 2023 functionality for both softwares.
- **Pricing:** A SelectHub comparison lists Navisworks starts at $96.63 per month and Revizto starts at $350 per month.
- **Ratings:** G2 reviewers give Navisworks a 9.2 for clash detection, from only 6 reviews, against Revizto's 7.5 from 31 reviews. The sample is small.
- **Other options:** Listings name Tekla Structures, Trimble Connect, BIMCollab, and STAAD as alternatives, and Solibri appears in several lists. None of the results compared false-positive rates.

I found no source that directly measures Navisworks false positives against Revizto or Solibri, or that confirms a 2025 shift in tool quality. Those points would need a search aimed at BIM practitioner forums or independent benchmarks.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:12.291Z

<details><summary>نتيجة أداة (3614 حرف)</summary>

```
Web search results for query: "IFC export Revit problems data loss interoperability complaints buildingSMART forum IFC5 2025"

Links: [{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/fix-ifc-export-errors/idc-p/13075799"},{"title":"revit 2024 enhancements to ifc geometric fidelity","url":"https://www.autodesk.com/blogs/aec/2023/07/24/revit-2024-enhancements-to-ifc-geometric-fidelity/?redirected=1"},{"title":"revit 2024 enhancements to ifc geometric fidelity","url":"https://www.autodesk.com/blogs/aec/2023/07/24/revit-2024-enhancements-to-ifc-geometric-fidelity/"},{"title":"community.graphisoft.com","url":"https://community.graphisoft.com/t5/Collaboration-with-other/IFC-Data-exchange-with-Revit/td-p/292531"},{"title":"Collaboration with other software","url":"https://community.graphisoft.com:443/t5/Collaboration-with-other/IFC-Data-exchange-with-Revit/m-p/292533"},{"title":"ifc for the win","url":"https://augi.com/articles/detail/ifc-for-the-win"},{"title":"About Revit and IFC","url":"https://help.autodesk.com/cloudhelp/2025/ENU/Revit-DocumentPresent/files/GUID-6708CFD6-0AD7-461F-ADE8-6527423EC895.htm"},{"title":"community.graphisoft.com","url":"https://community.graphisoft.com/t5/Collaboration-with-other/Revit-IFC-to-Archicad-is-fundamentally-flawed/m-p/590036"},{"title":"2020-02-07 04:31 PM","url":"https://community.graphisoft.com/t5/Collaborate-forum/IFC-Data-exchange-with-Revit/m-p/292531/highlight/true"},{"title":"About Revit and IFC","url":"https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-6708CFD6-0AD7-461F-ADE8-6527423EC895.htm"}]

The search turned up user complaints about Revit's IFC export, mostly from Autodesk and Graphisoft community forums. It found nothing about IFC5 and no buildingSMART forum threads.

**Export problems reported by users:**
- In an Autodesk Revit Ideas post, a user describes properties missing from IFC output, workset values exported incorrectly, and some elements appearing in the wrong place with no export error. The same post says a circular wall opening caused the whole wall to shift in the IFC. The quality of the IFC export needs to be fixed. The problem is with both properties and geometry. Other commenters reported floors and walls that were not exported at all.
- A Graphisoft community thread says Revit-to-ArchiCAD IFC exchange is seriously flawed. The result is barely usable without a lot of work to fix it. A developer there attributed the problem to Revit: it seems Revit exports these kinds of walls as BREPs, which the ArchiCAD add-in could not fully correct.
- Those BREP conversions occur because every time you have geometry that is not a strict extruded shape, it will become BREP.

**Context from Autodesk and others:**
- Autodesk states that Revit provides fully certified IFC import and export based on buildingSMART® IFC data exchange standards. Its 2025 help lists export support for IFC4, IFC2x3, and IFC2x2.
- Autodesk's own blog says when it comes to interoperability, data integrity is critical.
- An AUGI article notes that in April 2024, IFC 4.3 was released and is supported by Revit 2025.

**Gaps:** The results contain no IFC5-specific complaints, and no buildingSMART forum threads. The Autodesk post and the Graphisoft threads are user reports, not verified bug data. The Graphisoft threads are also older, and the Autodesk post cites Revit 2025.3. A follow-up search aimed at buildingSMART community or IFC5 pages would be needed to cover those.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:13.759Z

<details><summary>نتيجة أداة (4167 حرف)</summary>

```
Web search results for query: "ArcGIS Pro credits licensing cost complaints switch to QGIS users 2025 QGIS pain points"

Links: [{"title":"ArcGIS Pro Concurrent licensing retiring","url":"https://community.esri.com/t5/arcgis-pro-questions/arcgis-pro-concurrent-licensing-retiring/m-p/1509573"},{"title":"ArcGIS Pro Concurrent licensing retiring","url":"https://community.esri.com/t5/arcgis-pro-questions/arcgis-pro-concurrent-licensing-retiring/m-p/1382164"},{"title":"ArcGIS Pro Concurrent licensing retiring","url":"https://community.esri.com/t5/arcgis-pro-questions/arcgis-pro-concurrent-licensing-retiring/m-p/1382893"},{"title":"ArcGIS Pro Concurrent licensing retiring","url":"https://community.esri.com/t5/arcgis-pro-questions/arcgis-pro-concurrent-licensing-retiring/m-p/1382113"},{"title":"Select to view content in your preferred language","url":"https://community.esri.com/t5/arcgis-pro-ideas/feedback-on-arcgis-pro-licensing-changes-and/idc-p/1644797"},{"title":"g2.com","url":"https://g2.com/products/arcgis-pro/reviews?page=2"},{"title":"Pricing for ArcGIS Pro","url":"https://esri.com/en-us/store/arcgis-pro"},{"title":"arcmap is dead great time to switch to qgis","url":"https://www.lutraconsulting.co.uk/blogs/arcmap-is-dead-great-time-to-switch-to-qgis"},{"title":"Типы лицензий ArcGIS Pro","url":"https://doc.esri.com/ru/arcgis-pro/latest/get-started/licensing-arcgis-pro.html"},{"title":"community.esri.com","url":"https://community.esri.com/t5/arcgis-pro-questions/clarity-on-annual-subscriptions-for-arcgis-pro-and/td-p/1339693"},{"title":"ArcGIS Pro Licensing Change","url":"https://uwm.edu/information-technology/arcgis-pro-licensing-change/"},{"title":"Pricing for ArcGIS Pro","url":"https://www.esri.com/en-us/arcgis/products/arcgis-pro/levels"},{"title":"ArcGIS Pro licensing","url":"https://pro.arcgis.com/en/pro-app/get-started/about-licensing.htm"},{"title":"www.esri.com","url":"https://www.esri.com/arcgis-blog/wp-json/wp/v2/blog/70891"}]

The search turned up mostly ArcGIS-side complaints about cost and licensing, with less on QGIS pain points.

**Licensing and cost complaints:**
- Esri's concurrent-use licensing ended. Esri's documentation says that the Concurrent Use license type was deprecated on July 1, 2025.
- In an Esri Community thread, one county reported that its 2025 maintenance renewal would rise by about $8,000 and that its flexible concurrent licenses were being swapped for named seats. That poster said they had not seriously considered QGIS, but may face no choice.
- A G2 review summary lists high cost of ArcGIS Pro licensing among user dislikes, and says some essential features require additional payments or credits.
- A Brazilian micro-business user argued that the official reseller charges more than twice the international price.
- On credits specifically, Esri says that credits are the currency used in ArcGIS Online to purchase premium services, and that credits are included within each user type.

**QGIS side:**
- A Lutra Consulting blog (a QGIS services vendor, so it is promotional) frames the choice around cost, control, and lock-in. It notes that ArcGIS Pro requires an active subscription. When you stop paying, you stop working. It also concedes that with QGIS you will not get a free trip to San Diego every year.
- The main technical gap it names is that QGIS cannot connect to SDE directly, which matters for Esri enterprise geodatabases.
- Esri Community users who are moving toward QGIS still rely on ArcGIS for some work. One said they use QGIS where possible but have some particular tools in ArcGIS developed for analysis workflows or for things like map series that we don't want to (and in some cases can't) redevelop in QGIS.
- A G2 review also says that some features in ArcGIS Pro aren't available in free open-source alternatives like QGIS.

**Gaps:** I found no survey or systematic source on QGIS user pain points for 2025. The QGIS evidence here is vendor marketing and scattered forum comments. Esri's own pricing page is the primary source on credits and user types.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:14.204Z

<details><summary>نتيجة أداة (4760 حرف)</summary>

```
Web search results for query: "Nordic architects open letter Autodesk 2023 data ownership cloud lock-in Forma "Future AEC Software Specification" AEC Magazine"

Links: [{"title":"22 minute read","url":"https://issuu.com/x3dmedia/docs/aec_q3_2022/s/16813805"},{"title":"community.graphisoft.com","url":"https://community.graphisoft.com:443/gowhw84577/attachments/gowhw84577/ideas/21179/1/OPEN%20LETTER%20TO%20AUTODESK.pdf"},{"title":"220905 AiN Autodesk (002)","url":"https://enr.com/ext/resources/2022/09/16/220905_AiN_Autodesk-(002).pdf"},{"title":"Autodesk Open Letter","url":"https://aecmag.com/?p=15454"},{"title":"Autodesk Open Letter","url":"https://aecmag.com/bim/a-tale-of-two-open-letters/"},{"title":"architosh.com","url":"https://architosh.com/2022/10/the-revit-open-letter-through-the-lens-of-qwerty-nomics/amp"},{"title":"nordic letter aecmag.com","url":"https://www.trxl.co/content/files/nordic-letter-aecmag.com.pdf"},{"title":"architosh.com","url":"https://architosh.com/2022/10/the-revit-open-letter-through-the-lens-of-qwerty-nomics/3/"},{"title":"11 minute read","url":"https://issuu.com/x3dmedia/docs/aec_q3_2022/s/16813804"},{"title":"Autodesk Letter v3, this time from the Nordic architecture associations","url":"https://community.osarch.org/discussion/1130/"},{"title":"nordic architects open letter reignites scorching autodesk criticism","url":"https://www.archinect.com/news/article/150324438/nordic-architects-open-letter-reignites-scorching-autodesk-criticism"},{"title":"Nordic Autodesk letter","url":"https://aecmag.com/bim/nordic-architectural-associations-demand-better-value-from-autodesk"},{"title":"the revit open letter through the lens of qwerty nomics","url":"https://architosh.com/2022/10/the-revit-open-letter-through-the-lens-of-qwerty-nomics/"},{"title":"OSArch Community","url":"https://community-test.osarch.org/thread/1130/p1"},{"title":"architosh.com","url":"https://architosh.com/2022/10/the-revit-open-letter-through-the-lens-of-qwerty-nomics/2/"},{"title":"autodesk.com","url":"https://channelnews.autodesk.com/images/nod_img_store/4FC980A36F32D7FB9709.pdf"},{"title":"Back to the Future","url":"https://blogs.autodesk.com/forma/?p=1999"},{"title":"Autodesk: beyond the seat, the meter","url":"https://aecmag.com/ai/autodesk-beyond-the-seat-the-meter/"},{"title":"blogs.autodesk.com","url":"https://blogs.autodesk.com/forma/wp-json/wp/v2/posts/1999"}]

I ran one search. It confirmed the Nordic letter and its main complaints, but returned nothing on a "Future AEC Software Specification," so I can't verify that document.

- **Who signed:** The letter came from four professional bodies in Denmark, Finland, Iceland and Norway, representing about 14,000 architects. Signers included BIG, Snøhetta, Schmidt Hammer Lassen and 3XN. (Sources list the Danish, Norwegian, Finnish and Icelandic bodies, and name BIG, Snøhetta, Schmidt Hammer Lassen, and 3XN among the signatories.)
- **Timing:** It was an update to the 2020 UK-led letter. AEC Magazine's coverage dates it to 2022, and the letter's PDF is dated September 2022, not 2023. (The letter was from the Danish, Norwegian, Finnish and Icelandic architectural associations.)
- **Data ownership:** The letter argues that Autodesk's roadmap implies interoperability only if customers let Autodesk take ownership of their data, which the signers consider unacceptable as a long-term strategy. (The opening paragraph suggests Autodesk's roadmap assumes interoperability requires customers to cede data ownership, a model the signers see as unusual compared with other industries.)
- **Open standards:** The letter asks for better support for open data standards so that collaboration and data referencing work across non-Autodesk platforms. (Its requests include open data standards support for free collaboration across non-Autodesk platforms.)
- **Development complaints:** The letter says there has been little substantive progress in Autodesk's core products since the first letter. (The letter states that almost two years after the first letter, there is no substantial progress in Autodesk's core products.)
- **Forma:** Autodesk presents Forma as the place where project knowledge accumulates. Analysts noted that there remains a lack of detail about how soon Forma may address some of the issues addressed by the Open Letter firms.

The AEC Magazine articles most relevant to your query are "A tale of two open letters" and "Nordic architectural associations demand better value from Autodesk." I did not find any source tying the letter to a "Future AEC Software Specification," so that document may be a separate item you'll need to check directly.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:16.062Z

<details><summary>نتيجة أداة (5094 حرف)</summary>

```
Web search results for query: "PlanSwift CostX Bluebeam takeoff software complaints Windows only expensive learning curve AI takeoff 2025 reviews"

Links: [{"title":"# Page 2 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/%3Fpage%3D2"},{"title":"# Page 4 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/%3Fpage%3D4"},{"title":"# PlanSwift Reviews","url":"https://www.g2.com/products/PlanSwift/reviews"},{"title":"# Page 2 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=2"},{"title":"# Page 6 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=6"},{"title":"# Page 13 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=13"},{"title":"# PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://capterra.com/p/70808/PlanSwift/reviews/"},{"title":"# Bluebeam, PlanSwift vs STACK Takeoff &amp; Estimate Comparison","url":"https://www.g2.com/compare/bluebeam-vs-planswift-vs-stack-takeoff-estimate"},{"title":"www.softwareadvice.com","url":"https://www.softwareadvice.com/construction/planswift-takeoff-estimating-profile/reviews/"},{"title":"# Page 10 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=10"},{"title":"# Page 8 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=8"},{"title":"# PlanSwift Software 2026: Features, Integrations, Pros & Cons | Capterra","url":"https://capterra.com/p/70808/PlanSwift"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/10027215/zzTakeoff/reviews/"},{"title":"# Page 15 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=15"},{"title":"# Page 7 | PlanSwift Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/70808/PlanSwift/reviews/?page=7"},{"title":"Introducing G2.ai, the future of software buying.Try now","url":"https://www.g2.com/compare/bluebeam-vs-planswift"},{"title":"# Page 5 | STACK Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/147181/STACK-Takeoff/reviews/?page=5"},{"title":"www.capterra.ca","url":"https://www.capterra.ca/software/70808/planswift"}]

I ran one search. It returned plenty on PlanSwift and Bluebeam, but nothing on CostX, and nothing that confirms the Windows-only claim or specifically addresses learning curve.

**Ratings:** On G2, Bluebeam scores 4.5 out of 5, PlanSwift 4.3 out of 5, and STACK Takeoff & Estimate 4.4 out of 5. The takeoff-category scores are Bluebeam 8.5/10 (54 reviews), PlanSwift 7.8/10 (9 reviews), and STACK 7.6/10 (23 reviews). PlanSwift's sample is small, so treat these numbers cautiously.

**PlanSwift complaints:**
- **Licensing change:** The most pointed complaint is about pricing. One 2025 reviewer said the vendor stopped supporting perpetual licenses and required an annual subscription fee to "support" the license. G2 lists a different model, a one-time fee for a lifetime license with updates and support, at $1,595, so pricing terms may differ by customer or have changed.
- **Data and uploads:** G2's summary notes that users face frequent upload issues, leading to lost takeoff data when switching between PlanSwift versions.
- **Limits on PDFs:** One reviewer described the tool as limited to flat PDF documents, and another said that both methods are raster based so there is no intelligence for selecting lines, planes, etc.
- **Feature gaps versus Bluebeam:** A reviewer said that you can't split screens or extract pages like Bluebeam Revu and on-screen takeoff.

**PlanSwift praise and learning curve:** Reviewers mostly describe it as easy to pick up. One said they were able to navigate the program without a demo or training, and another noted that once assemblies are set up, quantity takeoffs are super easy. Assembly setup is where a learning curve would show up.

**AI:** One Capterra reviewer said the software has AI built in. I did not find details on what that AI does or how it compares with other tools' AI features.

**Bluebeam:** G2 rates its Collaborative Editing at 9.0 (43 reviews), while PlanSwift is listed as Feature Not Available in that category. Bluebeam is also more often praised for range of features than for simplicity.

**Gaps:** The results contain nothing on CostX, nothing confirming or refuting that PlanSwift or CostX are Windows-only, and no direct reviews of CostX's learning curve. A follow-up search focused on CostX reviews and platform support would fill those gaps.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-23T07:57:19.543Z

**أداة:** `WebSearch`

```json
{
 "query": "Snaptrude Arcol Qonic Motif Hypar browser-based BIM challengers 2025 2026 AEC Magazine next generation BIM",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:20.325Z

**أداة:** `WebSearch`

```json
{
 "query": "Speckle Rayon \"That Open Company\" open source AEC web BIM what they do 2025 funding",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:21.020Z

**أداة:** `WebSearch`

```json
{
 "query": "aecmag.com \"Autodesk: beyond the seat, the meter\" tokens AI consumption pricing customers",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:21.996Z

**أداة:** `WebSearch`

```json
{
 "query": "survey architects engineers AI 2025 what they want automate documentation drawings tedious tasks trust accuracy concerns AEC",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:22.902Z

**أداة:** `WebSearch`

```json
{
 "query": "Pix4D pricing complaints subscription expensive WebODM OpenDroneMap limitations memory large datasets ReCap Pro users",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:24.020Z

**أداة:** `WebSearch`

```json
{
 "query": "AutoCAD Plant 3D complaints isometrics spec editor slow project database users forum; Revit MEP duct pipe sizing limitations HVAC load calculation complaints",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:24.849Z

**أداة:** `WebSearch`

```json
{
 "query": "Revit file not backward compatible cannot save to previous version idea forum votes \"save as previous version\"",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:25.910Z

**أداة:** `WebSearch`

```json
{
 "query": "P6 XER import problems Microsoft Project conversion data loss schedulers POBS corrupt XER web-based XER viewer",
 "mode": "standard"
}
```

### user · 2026-11-23T07:57:31.146Z

<details><summary>نتيجة أداة (4319 حرف)</summary>

```
Web search results for query: "Revit file not backward compatible cannot save to previous version idea forum votes "save as previous version""

Links: [{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/m-p/6337733"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/idc-p/6571875/highlight/true"},{"title":"Backward compatibility of Revit with earlier releases of the software","url":"https://autodesk.com/support/technical/article/Backwards-compatibility-of-Revit-with-earlier-releases-of-the-software"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/idi-p/6337733/page/3"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/idc-p/7070756/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/idc-p/7459963"},{"title":"Request for save option to older version in revit","url":"https://forums.autodesk.com/t5/revit-architecture-forum/request-for-save-option-to-older-version-in-revit/td-p/12058618"},{"title":"Save family as previous version","url":"https://forums.autodesk.com/t5/revit-architecture-forum/save-family-as-previous-version/td-p/3345221"},{"title":"Revit 2018 in 2017","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-2018-in-2017/m-p/8827242"},{"title":"Autodesk Answer Days: SAVING TO OLDER REVIT VERSIONS?","url":"https://forums.autodesk.com/t5/revit-architecture-forum/autodesk-answer-days-saving-to-older-revit-versions/m-p/6334520"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/stop-annual-version-numbering/idi-p/9241676"},{"title":"Revit 2021 - Saving to a Previous Version","url":"https://forums.autodesk.com/t5/revit-mep-forum/revit-2021-saving-to-a-previous-version/m-p/9569168"},{"title":"Saving Revit file Back To A Previous Version","url":"https://forums.autodesk.com/t5/revit-architecture-forum/saving-revit-file-back-to-a-previous-version/m-p/3920617"},{"title":"Saving Revit Back To A Previous Version","url":"https://forums.autodesk.com/t5/revit-architecture-forum/saving-revit-back-to-a-previous-version/m-p/4673943"},{"title":"Revit 2021 - Saving to a Previous Version","url":"https://forums.autodesk.com/t5/revit-mep-forum/revit-2021-saving-to-a-previous-version/m-p/9546662"},{"title":"Revit Backwards Compatibility","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-backwards-compatibility/m-p/3291727/highlight/true"},{"title":"Saving Revit Back To A Previous Version","url":"https://forums.autodesk.com/t5/revit-architecture-forum/saving-revit-back-to-a-previous-version/m-p/2762474"}]

The search turned up the Autodesk Revit Ideas thread for "Save as previous version" and related discussions, but none of the results show the vote totals, so I can't confirm the count.

- **Official position:** Autodesk's support article says Revit does not have a feature to save to older version data formats or work with the newer RVT file format in an older version. It recommends workarounds such as exporting to IFC or DWG, and notes that this workflow still requires access to the newer version of Revit to open/export.
- **Why the idea was archived:** In one thread, a moderator archived the idea and said at least 14 of the top 20 ideas on this forum would require changes to the file format. A developer added that comparing our development build to the 2017 file, there are about 3,000 changes to the format.
- **Data-loss concern:** The same thread gives an example of the problem. Older versions don't understand newer data, so your arc wall would show up in Revit X as a linear wall!
- **Workaround:** Users on a subscription can typically install older releases. One Autodesk employee noted that if you are on subscription with Autodesk - you do get previous version use. Since you have 2012 you can use 2011, 2010 and 2009.
- **Community reaction:** Users argue that Microsoft database is backward compatible. Others point to AutoCAD, which has long offered a save-to-previous-version option, as a model.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.143Z

<details><summary>نتيجة أداة (3650 حرف)</summary>

```
Web search results for query: "Snaptrude Arcol Qonic Motif Hypar browser-based BIM challengers 2025 2026 AEC Magazine next generation BIM"

Links: [{"title":"snaptrude alternatives","url":"https://www.nomic.ai/compare/snaptrude-alternatives"},{"title":"Inside Motif: the agent-native BIM platform","url":"https://aecmag.com/bim/inside-motif-the-agent-native-bim-platform/"},{"title":"snaptrude ai conceptual design and beyond","url":"https://aecmag.com/bim/snaptrude-ai-conceptual-design-and-beyond/"},{"title":"qonic edges towards bim authoring","url":"https://aecmag.com/bim/qonic-edges-towards-bim-authoring/"},{"title":"BIM 2.0: unfinished business","url":"https://aecmag.com/bim/bim-2-0-unfinished-business/"},{"title":"SNAPTRUDE VS ARCHICAD 2026","url":"https://snaptrude.com/vs/archicad"},{"title":"60723 arcol brings bim to a browser gives design concept choice","url":"https://www.enr.com/articles/60723-arcol-brings-bim-to-a-browser-gives-design-concept-choice"},{"title":"snaptrude advances","url":"https://aecmag.com/bim/snaptrude-advances/"},{"title":"July 15, 2025","url":"https://www.snaptrude.com/blog/top-10-best-architecture-design-software-in-2025"},{"title":"aecmag.com","url":"https://aecmag.com/www. aecmag.com/tag/snaptrude"},{"title":"arcol unleashed bim 2 0","url":"https://aecmag.com/bim/arcol-unleashed-bim-2-0/"},{"title":"upFront.eZine #1,128: The Second Wave of BrowserCADs","url":"https://upfrontezine.substack.com/p/upfrontezine-1128-the-second-browsercad"},{"title":"Snaptrude launches version 3.0","url":"https://www.dezeen.com/2025/06/25/snaptrude-3-0/"},{"title":"Motif to take on Revit: exclusive interview","url":"https://aecmag.com/bim/motif-to-take-on-revit-exclusive-interview/"},{"title":"• | 9:00 am","url":"https://fastcompanyme.com/?p=99004"},{"title":"March 1, 2026","url":"https://www.snaptrude.com/blog/best-cloud-bim-software-2026"},{"title":"# Snaptrude says its new AI agent builds LoD 400 BIM models in minutes","url":"https://www.marketscale.com/industries/engineering-and-construction/snaptrude-says-its-new-ai-agent-builds-lod-400-bim-models-in-minutes.md"}]

The search turned up coverage of the main challengers, but little on Hypar and nothing dated specifically to late 2026 beyond a few items.

- **Shared framing:** AEC Magazine groups Snaptrude, Arcol, Qonic and Hypar as "BIM 2.0" applications, each rethinking BIM around cloud computing, modern data architectures and, latterly, AI. Motif is the newest entrant in that group.
- **Snaptrude:** AEC Magazine describes it as the first of the browser-based BIM 2.0 challengers. Its own 2026 materials pitch it as a cloud-native tool for early-stage design. Treat those self-descriptions with caution.
- **Arcol:** It focuses on an initial browser-based environment for collaborative conceptual design, and AEC Magazine notes that Motif and Snaptrude have copied its speed and capabilities.
- **Qonic:** AEC Magazine reports that Qonic is pushing its browser-based BIM platform further into authoring, with native components and a project-wide issues view. It is described as the most construction-facing of the group.
- **Motif:** AEC Magazine reports that Motif launches its BIM authoring platform and is browser-delivered. Its launch coverage is the most recent item in these results.
- **Hypar:** The results name it only in passing as part of the BIM 2.0 group. I found no 2025–2026 product details for it.

Next steps: a targeted search on Hypar's 2025–2026 status, or AEC Magazine's NXT BLD 2026 coverage, would fill the main gaps.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.151Z

<details><summary>نتيجة أداة (3573 حرف)</summary>

```
Web search results for query: "aecmag.com "Autodesk: beyond the seat, the meter" tokens AI consumption pricing customers"

Links: [{"title":"Autodesk: beyond the seat, the meter","url":"https://aecmag.com/ai/autodesk-beyond-the-seat-the-meter/"},{"title":"Monthly Flex tokens (beta)","url":"https://help.autodesk.com/cloudhelp/ENU/Fusion-CloudCredits/files/INCLUDED-QUOTA-TKNS.htm"},{"title":"Autodesk wants you to pay for outcomes, not just access","url":"https://schnitgercorp.com/2025/10/08/autodesk-wants-you-to-pay-for-outcomes-not-just-access/"},{"title":"Capacity-based subscriptions","url":"https://www.autodesk.com/campaigns/capacity"},{"title":"Capacity-based subscriptions","url":"https://www.autodesk.com/content/autodesk/global/en/campaigns/capacity"},{"title":"Autodesk wants you to pay for outcomes, not just access","url":"https://schnitgercorp.com/2025/10/08/autodesk-wants-you-to-pay-for-outcomes-not-just-access/amp/"},{"title":"the 3 biggest autodesk ai takeaways from au 2025","url":"https://adsknews.autodesk.com/en/news/the-3-biggest-autodesk-ai-takeaways-from-au-2025/"},{"title":"Autodesk til mindre virksomheder","url":"https://www.autodesk.com/dk/small-business"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=54116"},{"title":"3 Sep 2026","url":"https://aps.autodesk.com/blog/data-model-apis-included-subscriptions-plus-flexible-ways-scale"},{"title":"Autodesk for small business","url":"https://www.autodesk.com/ae/small-business"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=55233"},{"title":"15 Sep 2025","url":"https://aps.autodesk.com/node/3776"},{"title":"& Construction","url":"https://www.autodesk.com/content/autodesk/global/en/buying/flex/flex-rate-sheet"},{"title":"Key Learnings","url":"https://autodesk.com/autodesk-university/class/Why-You-Need-Both-Flex-and-Subscription-2024"},{"title":"www.autodesk.com","url":"https://www.autodesk.com/products/fusion-360/blog/?p=93064"},{"title":"27 Oct 2026","url":"https://aps.autodesk.com/node/3881"}]

The AECMag piece argues that Autodesk is keeping the named-user seat and layering consumption pricing on top of it, rather than replacing seats. The search returned only part of the article, so the rest of its argument is not visible here.

- **Seat retained, consumption added:** AECMag reads Autodesk University 2026 as signalling that the seat stays while adding consumption above it. It also reports that Autodesk told us that every automation machine requires a licensed named-user seat. The author says the precise licensing boundary remains unclear.
- **Portability concern:** The article asks Autodesk to clarify whether customers' accumulated knowledge can move with them if they leave.
- **Token mechanics in Fusion (Autodesk help):** Monthly Flex tokens (beta) begin rolling out to Fusion subscribers from September 30, 2026, with tokens included for each seat. One monthly Flex token (beta) gives you 120 AI assists. On multi-seat plans, the allowance is shared by everyone on the team.
- **Pricing context from 2025 commentary:** Schnitger Corp notes that 17% of fiscal 2025 revenue was already consumption-based, mostly from enterprise agreements, and that actual outcome-based pricing had not been published at the time.
- **Cloud API tokens:** For Autodesk Platform Services, usage is measured in tokens and billed according to the APS rate table for EBA customers without an eligible product subscription.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.336Z

<details><summary>نتيجة أداة (3917 حرف)</summary>

```
Web search results for query: "Speckle Rayon "That Open Company" open source AEC web BIM what they do 2025 funding"

Links: [{"title":"3D rendering of a hand draw architecture project with a tablet showing the finished house","url":"https://techcrunch.com/?p=2300391"},{"title":"Company news","url":"https://www.speckle.systems/blog/speckle-raises-12-5-million-to-build-the-first-aec-data-hub"},{"title":"www.cbinsights.com","url":"https://www.cbinsights.com/company/speckle"},{"title":"3D rendering of a hand draw architecture project with a tablet showing the finished house","url":"https://techcrunch.com/2022/04/14/speckle-snags-5-5m-seed-to-build-open-source-platform-for-3d-drawings/?rand=23331"},{"title":"growing the speckle seed","url":"https://speckle.systems/blog/growing-the-speckle-seed"},{"title":"Software Sparks Success | Open Source Speckle Raises Series A For AEC","url":"https://www.foundamental.com/perspectives/software-sparks-success-open-source-speckle-raises-series-a-for-aec"},{"title":"speckle the open source cloud data platform","url":"https://aecmag.com/data-management/speckle-the-open-source-cloud-data-platform/"},{"title":"speckle the open source cloud data platform","url":"https://aecmag.com/features/speckle-the-open-source-cloud-data-platform/"},{"title":"3D rendering of a hand draw architecture project with a tablet showing the finished house","url":"https://techcrunch.com/2022/04/14/speckle-snags-5-5m-seed-to-build-open-source-platform-for-3d-drawings"},{"title":"speckle matures","url":"https://aecmag.com/collaboration/speckle-matures/"},{"title":"Speckle Raises $12.5 Million to Build The First AEC Data Hub","url":"https://foundamental.com/perspectives/speckle-raises-12-5-million-to-build-the-first-aec-data-hub"},{"title":"simplify.jobs","url":"https://simplify.jobs/c/Speckle"},{"title":"Building What’s Next: Agent Workflows in Speckle","url":"https://speckle.systems/blog"},{"title":"DiscoverArchi-Tech NetworkEP 57 | The Rise of Speckle w/ Dimitrie Stefanescu & Matteo Cominetti","url":"https://castbox.fm/episode/EP-57-|-The-Rise-of-Speckle-w-Dimitrie-Stefanescu-%26-Matteo-Cominetti-id4623680-id770289335"},{"title":"Total Raised","url":"https://www.cbinsights.com/company/speckle/financials"},{"title":"That Open Company","url":"https://aecmag.com/software/that-open-company-raises-the-stakes/"},{"title":"pc.st","url":"https://pc.st/e/.QFxmNk5gWH"},{"title":"Foundamental LogoFoundamental Logo","url":"https://university.foundamental.com/glossary/open-source-construction-speckle-dimitrie-stefanescu/"}]

I ran one search. It covered Speckle well but turned up no funding information for That Open Company.

**Speckle**
- Speckle is an open-source data platform for AEC. It runs an open-core model, with much of the development time going to the open-source core and a proprietary enterprise layer on top. Speckle describes itself as an open source data platform for AEC. The company operates on an open core model.
- Its funding dates conflict across sources. Speckle's own blog dates its $12.5M raise to Jun 24, 2025, while Foundamental's coverage is dated October 25, 2024 and describes the round as a $12.5M Series A led by Addition.
- Simplify Jobs lists Total Funding $18M, and a later item says Suffolk Technologies invests in Speckle. That item is dated April 2026 in the same listing.

**That Open Company**
- The only relevant source is an AEC Magazine article. It says That Open Platform is a BIM operating system rather than another BIM tool. The firm was earlier best known for IFC.js, a browser-based open source IFC toolkit. It also reports a wider community of over 10,000 developers building on its open-source work.
- No funding details for That Open Company appeared in these results, so I can't confirm any 2025 funding from this search.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.348Z

<details><summary>نتيجة أداة (5503 حرف)</summary>

```
Web search results for query: "P6 XER import problems Microsoft Project conversion data loss schedulers POBS corrupt XER web-based XER viewer"

Links: [{"title":"My Oracle Support Banner","url":"https://support.oracle.com/knowledge/Oracle%20Cloud/2204861_1.html"},{"title":"p6 pro importing exporting","url":"https://docs.oracle.com/cd/F74771_01/English/admin/p6_pro_importing_exporting/p6_pro_importing_exporting.pdf"},{"title":"ms project import export data map xml","url":"https://docs.oracle.com/cd/F74771_01/English/Mapping_and_Schema/ms_project_import_export_data_map_xml/ms_project_import_export_data_map_xml.pdf"},{"title":"Primavera (MOSC)","url":"https://community.oracle.com/mosc/discussion/4550885/why-is-p6-udf-data-missing-after-import-from-ms-project-uids"},{"title":"p6 pro importing exporting","url":"https://docs.oracle.com/cd/F51303_01/English/admin/p6_pro_importing_exporting/p6_pro_importing_exporting.pdf"},{"title":"p6 pro importing exporting","url":"https://docs.oracle.com/cd/F25600_01/English/admin/p6_pro_importing_exporting/p6_pro_importing_exporting.pdf"},{"title":"Primavera (MOSC)","url":"https://community.oracle.com/mosc/discussion/4550885/hhttps:/us.v-cdn.net"},{"title":"Primavera (MOSC)","url":"https://community.oracle.com/mosc/discussion/4512659/primavera-p6-import-event-ucvft-1399-d"},{"title":"docs.oracle.com","url":"https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/ms_project_import_export_data_map_xml/97782.htm"},{"title":"support.oracle.com","url":"https://support.oracle.com/knowledge/Oracle%20Cloud/2362227_1.html"},{"title":"Import a Microsoft Project file","url":"https://docs.oracle.com/cd/F51303_01/English/admin/p6_pro_importing_exporting/import_a_microsoft_project_file.htm"},{"title":"About Microsoft Project Import/Export Data Map Guide (XML)","url":"https://docs.oracle.com/cd/F74773_01/English/Mapping_and_Schema/ms_project_import_export_data_map_xml/97782.htm"},{"title":"Considerations for Importing Microsoft Project Files (MPP, MPX, XML) into P6 and Contractor","url":"https://support.oracle.com/knowledge/More%20Applications%20and%20Technologies/903268_1.html"},{"title":"Import a Microsoft Project file","url":"https://docs.oracle.com/cd/F25600_01/English/admin/p6_pro_importing_exporting/import_a_microsoft_project_file.htm"},{"title":"ms project import export data map xml","url":"https://docs.oracle.com/cd/F88966_01/English/Mapping_and_Schema/ms_project_import_export_data_map_xml/ms_project_import_export_data_map_xml.pdf"},{"title":"XER Import Is Slow / Hangs When Importing Risk Category or XER Conversion to SDEF Fails","url":"https://support.oracle.com/knowledge/More%20Applications%20and%20Technologies/2413071_1.html"},{"title":"Error: \"A Version x.x.x XER File Cannot Be Imported\" When Importing An XER Into P6 Professional","url":"https://support.oracle.com/knowledge/More%20Applications%20and%20Technologies/904651_1.html"},{"title":"You can import and export between P6 Professional and other applications using the following file formats:","url":"https://docs.oracle.com/cd/F37128_01/English/admin/p6_pro_importing_exporting/import_export_file_formats.htm"},{"title":"My Oracle Support Banner","url":"https://support.oracle.com/knowledge/Oracle%20Cloud/2934677_1.html"}]

The search turned up Oracle documentation and support threads on XER import and conversion problems. It did not cover POBS, corrupt-XER repair, or web-based XER viewers, so those parts of your query are unanswered.

- **Data loss in Microsoft Project conversion:** Oracle's mapping guide says P6 and MS Project use different data structures, so some information can be lost in a round trip. It also notes that unit and cost calculations can differ between the two tools. (P6 EPPM and P6 Professional use different data structures from Microsoft Project, so some information may be lost during the import and export process.)
- **Microsoft Project XML route:** Oracle says importing an MS Project XML file that came from P6 Professional is not supported, because ProjectLink was removed. (Since ProjectLink was removed from P6 Professional, importing a Microsoft Project XML file that was exported from P6 Professional is not supported.) Oracle's support notes also describe P6-exported XML that fails to open in Microsoft Project with a "problem with this file" error. (index 10-1, 10-2)
- **UDF loss:** One MOSC thread reports P6 user-defined field data going missing after an MS Project UID import. (index 4-1)
- **XER import failures:** Oracle's support note describes a case where projects import but no activities come through. (index 1-1) Another note covers P6 Web XER imports failing with a "Job failed" error. (index 19-1)
- **Slow or hung imports:** Oracle documents XER imports that stall on Risk Category, and XER-to-SDEF conversions that produce a blank output file. (index 16-1, 16-2, 16-3)
- **Partial commits:** Oracle's comparison of import formats says XER can end up with partial commits, while XML rolls back on failure. (index 18-8, 18-9)
- **Version errors:** A "version x.x.x XER file cannot be imported" error appears when importing into P6 Professional. (index 17-1)

Oracle's Doc IDs (2204861.1, 2934677.1, 2413071.1, 904651.1) are the best starting points if you have My Oracle Support access. The search did not return anything on POBS or on web-based XER viewers, so those would need a separate search.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.652Z

<details><summary>نتيجة أداة (4590 حرف)</summary>

```
Web search results for query: "Pix4D pricing complaints subscription expensive WebODM OpenDroneMap limitations memory large datasets ReCap Pro users"

Links: [{"title":"Why Do Pix4Dcloud Projects Fail During Point Cloud Generation on Large Image Sets?","url":"https://community.pix4d.com/t/why-do-pix4dcloud-projects-fail-during-point-cloud-generation-on-large-image-sets/33771"},{"title":"What is your biggest pain with ODM / OpenSfM?","url":"https://community.opendronemap.org/t/what-is-your-biggest-pain-with-odm-opensfm/25791?page=2"},{"title":"community.pix4d.com","url":"https://community.pix4d.com/t/pix4d-cloud-processing-costs-doubled/27426"},{"title":"Pix4D Cloud Processing Costs Doubled?","url":"https://community.pix4d.com/t/pix4d-cloud-processing-costs-doubled/27426/3"},{"title":"r/UAVmapping 15d ago","url":"https://redlib.hackliberty.org/r/UAVmapping/comments/1l5dkqp/webodm/mwixi1q/?context=3"},{"title":"support.pix4d.com","url":"https://support.pix4d.com/hc/en-us/articles/215858503?hsLang=en"},{"title":"Peer-reviewed paper comparing Metashape, Pix4D, WebODM, Correlator3D","url":"https://community.opendronemap.org/t/peer-reviewed-paper-comparing-metashape-pix4d-webodm-correlator3d/10187"},{"title":"r/UAVmapping 16d ago","url":"https://pol1.lr.ggtyler.dev/r/UAVmapping/comments/1l5dkqp/webodm/mwit6d5/?context=3"},{"title":"r/UAVmapping 12d ago","url":"https://redlib.hackliberty.org/r/UAVmapping/comments/1l5dkqp/webodm/mwpkyhg/?context=3"},{"title":"support.pix4d.com","url":"https://support.pix4d.com/hc/en-us/articles/215858503"},{"title":"pix4dmatic 2 deep dive","url":"https://aerocartwright.pages.dev/blog/pix4dmatic-2-deep-dive/"},{"title":"support.pix4d.com","url":"https://support.pix4d.com/hc/en-us/articles/360056382772"},{"title":"RAM requirements and cloud based processing","url":"https://community.opendronemap.org/t/ram-requirements-and-cloud-based-processing/7199"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/234673/PIX4Dmapper/"},{"title":"community.pix4d.com","url":"https://community.pix4d.com/t/why-can-i-not-renew-my-monthly-subscription-it-asks-if-i-want-to-be-on-a-waiting-list/26731"},{"title":"pix4d vs metashape vs webodm vs realitycapture","url":"https://aerocartwright.pages.dev/blog/pix4d-vs-metashape-vs-webodm-vs-realitycapture/"},{"title":"# Pix4D Review: Is the Industry Standard Worth the Price and Complexity?","url":"https://www.skyebrowse.com/news/posts/pix4d-review.md"},{"title":"webodm review","url":"https://www.skyebrowse.com/news/posts/webodm-review"}]

The results cover Pix4D pricing, WebODM memory limits, and large-dataset behavior, but nothing on ReCap Pro specifically. Most sources are forum posts or blogs, so treat them as anecdotal.

**Pix4D pricing:** Pricing isn't published for most tiers. One blog says Pix4D does not publish numbers publicly for Analyst and Pro perpetual pricing, and you negotiate directly. Another notes that the sales process involves a quote rather than a self-serve checkout for most configurations. A Pix4D community reply describes the pricing provides good value, relative to the competition for medium-sized customers, so opinions differ.

**WebODM limitations:**
- Memory: one OpenDroneMap forum thread reports that the most common failure is due to lack of memory, and a blog says a 5,000-image project that Metashape or Pix4D handles routinely will need significant RAM tuning and processing time adjustment in ODM.
- Chunking: a user notes that Metashape's chunking feature allows us to process large datasets much more efficiently than WebODM, which lacks a similar native option, and suggests ClusterODM as a workaround.
- Ground control: a commenter says the ground control process of WebODM alone cost too much time in the workflow to be viable.
- Hidden cost: one review says the Lightning cloud option introduces per-job pricing, which scales unpredictably with project volume.

**Large datasets on commercial tools:** Pix4D isn't immune. One Reddit user says Even Pix4d and Metashape buckle under large high resolution projects. A blog says PIX4Dmatic 2.0 handles large datasets — 5,000+ images — without the manual block-splitting that Mapper required. It also reports that AMD graphics falls back to CPU-only processing. That is painfully slow on large datasets.

**Gap:** Nothing in these results addresses ReCap Pro (Autodesk) pricing, limits, or user complaints. A follow-up search on ReCap Pro would be needed for that part of your question.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:32.914Z

<details><summary>نتيجة أداة (4827 حرف)</summary>

```
Web search results for query: "survey architects engineers AI 2025 what they want automate documentation drawings tedious tasks trust accuracy concerns AEC"

Links: [{"title":"cranes work with the sun on the horizon in the background Bechtel","url":"https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/12/18/architecture-engineering-construction-sector-slow-to-adapt-ai-survey-shows"},{"title":"UpCodes State of AI AEC Report 2026","url":"https://marketing.up.codes/hubfs/Reports/UpCodes_State_of_AI_AEC_Report_2026.pdf"},{"title":"New research explores perceptions and opportunities of artificial intelligence in architecture","url":"https://www.aia.org/index%2ephp/about-aia/press/new-research-explores-perceptions-and-opportunities-artificial-intelligence"},{"title":"New research explores perceptions and opportunities of artificial intelligence in architecture","url":"https://www.aia.org/index%2Ephp/about-aia/press/new-research-explores-perceptions-and-opportunities-artificial-intelligence"},{"title":"New research explores perceptions and opportunities of artificial intelligence in architecture","url":"https://www.aia.org/about-aia/press/new-research-explores-perceptions-and-opportunities-artificial-intelligence"},{"title":"bentley survey ai data security aec firms","url":"https://www.bentley.com/en/blog/bentley-survey-ai-data-security-aec-firms/"},{"title":"OCT 15, 2025","url":"https://www.bentley.com/blog/insights/ai-use-in-infrastructure-set-to-soar-as-firms-weigh-risks-and-returns/"},{"title":"What Architects Expect From AI Tools in 2026","url":"https://www.archdaily.com/en/1040024/what-architects-expect-from-ai-tools-in-2026"},{"title":"What Architects Expect From AI Tools in 2026","url":"https://www.archdaily.com/1040024/what-architects-expect-from-ai-tools-in-2026?video=true"},{"title":"photo of AI panel discussion Bentley Systems","url":"https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/12/08/ai-use-in-infrastructure-set-to-soar-as-firms-weigh-risks-and-returns"}]

The search turned up several 2025-era surveys, plus a few 2026 reports that are more current.

- **Documentation and tedious work:** Firms are mainly using or experimenting with AI to automate document-related processes and to improve design and engineering productivity, according to a Bentley-linked infrastructure survey Firms are now mainly using or experimenting with AI to automate document-related processes and to improve the productivity of design and engineering processes. In a Chaos/Architizer survey, architects who already see productivity gains in concept design think AI could eventually take over tedious construction-documentation work designers who are already experiencing productivity gains in concept design believe AI could eventually help automate tedious processes in construction documentation, freeing up time for more creative work.
- **Automating manual tasks:** In AIA's March 2025 study, architects were most optimistic about automating manual tasks, with 84% Architects are most optimistic about being able to automate manual tasks to save time and help with product research, according to 84 percent and 74 percent of respondents, respectively.
- **Adoption is still low:** A Bluebeam survey of 1,000 AEC professionals found only 27% of respondents use AI in their operations. AIA found that only 8 percent of firms have implemented AI solutions into their practice.
- **Trust and accuracy:** The 2026 UpCodes report ranks accuracy as a top barrier, with top three challenges to AI adoption: Data privacy or security concerns, Lack of knowledge/training, Uncertainty around accuracy. It cites 45% of professionals naming accuracy concerns as their top barrier, and says these concerns reflect the high-stakes nature of AEC work, where errors can have significant safety, financial, and legal implications. Architects who had not adopted AI pointed to output accuracy and reliability as a practical barrier.
- **Data security:** In a Bentley/AEC Advisors survey of more than 100 U.S. firms, nearly half of the companies polled strictly prohibit external vendors from using their data to train AI models.
- **Risk controls:** Over a third of infrastructure firms have limited or no project controls to manage risk where AI is used for design and construction.

Caveats: these surveys use different samples and definitions, and several are vendor-sponsored (Bluebeam, Bentley, Chaos, UpCodes), so treat the percentages as directional. The results I found don't include a single survey that ranks exactly what architects and engineers most want automated, so the documentation and drawing claims above are drawn from separate studies.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:33.254Z

<details><summary>نتيجة أداة (4352 حرف)</summary>

```
Web search results for query: "AutoCAD Plant 3D complaints isometrics spec editor slow project database users forum; Revit MEP duct pipe sizing limitations HVAC load calculation complaints"

Links: [{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/autocad-plant-3d-p-id-ideas/faster-iso-creation/m-p/5995883"},{"title":"autodesk.com","url":"https://forums.autodesk.com/t5/autocad-plant-3d-forum/slow-isogen/td-p/8161726"},{"title":"autodesk.com","url":"https://forums.autodesk.com:443/t5/autocad-plant-3d-p-id-ideas/faster-iso-creation/idi-p/5995883"},{"title":"& Construction","url":"https://autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Stub-end-won-t-be-rotated-in-AutoCAD-Plant-3D-2024-isometric-drawing.html"},{"title":"www.g2.com","url":"https://www.g2.com/products/autocad-p-id/reviews"},{"title":"AutoCAD Plant 3D Forum","url":"https://forums.autodesk.com/t5/autocad-plant-3d-forum/what-super-computer-questions-for-autocad-base-product/m-p/3313371"},{"title":"Top Troubleshooting Tips AutoCAD Plant 3D 2013","url":"https://www.autodesk.com/autodesk-university/class/Top-Troubleshooting-Tips-AutoCAD-Plant-3D-2013"},{"title":"autocad plant 3d","url":"https://www.selecthub.com/p/plm-software/autocad-plant-3d/"},{"title":"Things You Didnt Know Working More Efficiently AutoCAD Plant 3D and AutoCAD PID 2019","url":"https://www.autodesk.com/autodesk-university/class/Things-You-Didnt-Know-Working-More-Efficiently-AutoCAD-Plant-3D-and-AutoCAD-PID-2019"},{"title":"Poor performance on specific drawings in AutoCAD products","url":"https://autodesk.com/es/support/technical/article/Troubleshooting-poor-performance-with-specific-drawings-in-AutoCAD"},{"title":"g2.com","url":"https://g2.com/products/autocad-plant-3d/reviews"},{"title":"Slow or poor performance in AutoCAD Products","url":"https://knowledge.autodesk.com/article/Graphics-system-causes-slow-performance-in-AutoCAD"},{"title":"& Construction","url":"https://forums.autodesk.com/t5/autocad-plant-3d-forum/problems-with-the-ports-of-an-custom-element-in-isometric/td-p/12810989"},{"title":"What Now Things You Are Missing AutoCAD Plant 3D 2019","url":"https://www.autodesk.com/autodesk-university/class/What-Now-Things-You-Are-Missing-AutoCAD-Plant-3D-2019"},{"title":"Civil 3D Forum","url":"https://forums.autodesk.com/t5/civil-3d-forum/newer-features-slower-to-react-than-their-classic-counterparts/m-p/9293816"},{"title":"AutoCAD Plant 3D 2022 Known Issues","url":"https://help.autodesk.com/cloudhelp/2022/ENU/AutoCAD-ReleaseNotes/files/known_issues/AUTOCAD_PLNT3D_2022_KNOWN_ISSUES.html"}]

I ran one search, and it covered only the AutoCAD Plant 3D half. The Revit MEP duct/pipe sizing and HVAC load calculation complaints were not searched.

**AutoCAD Plant 3D complaints (from the results):**
- **Isometric generation is slow and needs manual cleanup.** A forum user says even quick Isometrics take a long time and we still have to manually edit them. Another describes a long-running request to limit production-mode isometric drops to a single selected model; that thread has sat under review for years.
- **Isogen/LDT performance.** One thread reports that the data-filling process is very slow, with a user noting that it is like it opens excel in the background for every field instead of once to read it all. Other users say LISP-based data filling is much faster.
- **General performance and memory.** A G2 review summary lists high memory usage with AutoCAD Plant 3D, leading to slow layout generation and performance issues. A long-time forum user compares it unfavorably with PDMS on zoom and orbit responsiveness.
- **Bugs and object enablers.** Reviewers mention software bugs in AutoCAD Plant 3D create challenges, particularly with object enablers being tricky to manage.
- **Balancing view.** Overall ratings are positive. G2 lists an average of 4.5/5.0 across 43 reviews, and one aggregator reports a 'great' User Satisfaction Rating of 88% based on 29 user reviews. Reviewers also cite limited structural modeling as a weakness compared with dedicated structural software.

**Revit MEP:** Not searched. A follow-up query on duct/pipe sizing limits and HVAC load calculation complaints would be needed to cover it.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-23T07:57:36.249Z

**أداة:** `WebSearch`

```json
{
 "query": "Revit MEP frustrations duct pipe routing sizing fabrication electrical circuits limitations engineers forum 2024 2025",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:37.139Z

**أداة:** `WebSearch`

```json
{
 "query": "Rayon design browser 2D CAD collaborative architects funding; Hypar 2025 text-to-BIM status",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:38.239Z

**أداة:** `WebSearch`

```json
{
 "query": "Revit on Mac no native version request Autodesk idea; Civil 3D LandXML export import problems interoperability",
 "mode": "standard"
}
```

### assistant · 2026-11-23T07:57:38.879Z

**أداة:** `WebSearch`

```json
{
 "query": "Coohom reviews complaints pricing render credits limitations Capterra G2",
 "mode": "standard"
}
```

### user · 2026-11-23T07:57:44.670Z

<details><summary>نتيجة أداة (3321 حرف)</summary>

```
Web search results for query: "Coohom reviews complaints pricing render credits limitations Capterra G2"

Links: [{"title":"Coohom Pricing Overview","url":"https://www.g2.com/products/coohom/pricing"},{"title":"Introducing G2.ai, the future of software buying.Try now","url":"https://www.g2.com/products/coohom-3d-visualization/pricing"},{"title":"coohom ai interior design review","url":"https://www.meltflexai.com/blog/coohom-ai-interior-design-review"},{"title":"ch.trustpilot.com","url":"https://ch.trustpilot.com/review/coohom.com"},{"title":"dk.trustpilot.com","url":"https://dk.trustpilot.com/review/coohom.com"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/192882/Coohom/reviews/"},{"title":"au.trustpilot.com","url":"https://au.trustpilot.com/review/coohom.com"},{"title":"se.trustpilot.com","url":"https://se.trustpilot.com/review/coohom.com"},{"title":"# Page 2 | Coohom Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/192882/Coohom/reviews/?page=2"},{"title":"zoftwarehub.com","url":"https://zoftwarehub.com/en-bh/products/coohom/reviews"},{"title":"www.capterra.com","url":"https://www.capterra.com/p/192882/Coohom/"},{"title":"www.capterra.co.uk","url":"https://www.capterra.co.uk/software/192882/coohom"},{"title":"www.g2.com","url":"https://www.g2.com/products/coohom"},{"title":"# Page 3 | Coohom Reviews 2026. Verified Reviews, Pros & Cons | Capterra","url":"https://www.capterra.com/p/192882/Coohom/reviews/?page=3"},{"title":"www.capterra.co.za","url":"https://www.capterra.co.za/reviews/192882/coohom"},{"title":"producthunt.com","url":"https://www.producthunt.com/posts/coohom/reviews"}]

Search results on Coohom are mixed, and I didn't find anything specific about render credits.

- **Pricing and renewals:** A third-party blog says Coohom's Trustpilot and Capterra reviews include recurring complaints about auto-renewal, with some users surprised by annual charges after monthly billing. Coohom has a free tier, with real limits, and three paid steps above it. Trustpilot reviewers call the pricing confusing, and one says the low entry price rises sharply once work must leave the platform (the lower plan attracts users, but the moment you want to use your work outside the platform, you are required to pay a much higher price). Capterra's UK listing shows Pro at $30/month monthly or $25/month yearly, and Premium at $100/month monthly or $83.34/month yearly.
- **Free-tier limits:** A Trustpilot reviewer describes Coohom as more expensive than Sketchup and Autocad, with hidden costs. Another review says the free version lacks essential tools needed for professional use.
- **Ratings:** G2 lists 174 reviews at 4.3 out of 5. Capterra lists 78 reviews at 4.8 out of 5. Capterra reviewers praise fast rendering and realistic output, and one notes realtime lighting is very expensive.
- **Other complaints:** Trustpilot reviewers mention a non-intuitive UI, weak customer service, and AI functions are borderlining sham.

The blog source is a competitor-style review, so treat its claims about renewal complaints as unverified. I didn't find the actual render-credit allowances, so check Coohom's current pricing page for those.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:44.973Z

<details><summary>نتيجة أداة (4231 حرف)</summary>

```
Web search results for query: "Revit MEP frustrations duct pipe routing sizing fabrication electrical circuits limitations engineers forum 2024 2025"

Links: [{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/revit-vs-navisworks-for-coordination/m-p/7654558"},{"title":"Copper R-410A HVAC Refrigeration Pipe/Line-Set Family & MEP Settings","url":"https://forums.autodesk.com/t5/revit-mep-forum/copper-r-410a-hvac-refrigeration-pipe-line-set-family-amp-mep/m-p/8974136"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/piping-sizing-shortcut/m-p/14270605"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/idb-p/revit-ideas-en/label-name/dynamo"},{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/bd-p/188/page/40"},{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/rectangular-offset-fitting-with-different-size-ducts/m-p/10917985/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/massive-overhaul-of-mep/idi-p/13798653"},{"title":"community.graphisoft.com","url":"https://community.graphisoft.com/t5/Collaboration-with-other/MEP-Modeler-Issues-and-Frustration/m-p/126708/highlight/true"},{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/duct-area-is-plain-wrong-or-am-i-missing-something/m-p/11434127"},{"title":"community.graphisoft.com","url":"https://community.graphisoft.com/t5/Collaboration-with-other/MEP-Modeler-Issues-and-Frustration/m-p/126707/highlight/true"},{"title":"Pipe connector issues, Flawed or fixable?","url":"https://forums.autodesk.com/t5/revit-mep-forum/pipe-connector-issues-flawed-or-fixable/m-p/8837195"},{"title":"Revit Fails and Fixes","url":"https://augi.com/articles/detail/revit-fails-and-fixes"},{"title":"Revit MEP Forum","url":"https://forums.autodesk.com/t5/revit-mep-forum/why-is-conduit-modeling-in-revit-so-terrible/m-p/9058015"},{"title":"Duct not showing in architectural model","url":"https://forums.autodesk.com/t5/revit-mep-forum/duct-not-showing-in-architectural-model/m-p/9699492"},{"title":"Open Discussion Current MEP Workflows Revit 2017","url":"https://www.autodesk.com/autodesk-university/class/Open-Discussion-Current-MEP-Workflows-Revit-2017"}]

The search turned up forum threads on Revit MEP pain points, but few are clearly from 2024–2025, and I found nothing specific to electrical circuits.

- **Sizing and calculations:** One engineer says it does do duct and pipe sizing, but engineering these systems is more complicated than what revit makes it. Another notes it lacks some calcs, including Vent sizing, Refrigerant System calcs, Gas or Compressed Air sizing. A 2025 user counters that You can do all the pipe and duct calcs in Revit.
- **Routing and fittings:** A 2025 (R2025.4) user says that for custom fittings, Automatic routing is not a reliable solution. Long runs are awkward: a user says the system wasn't built to do this very quickly. Pipe connector size mismatches with routing preferences also trigger errors, per a thread on Mitsubishi line-set families.
- **Recent Revit 2027 complaints:** An Autodesk Ideas thread reports that the Options Bar was removed, which used to let MEP users quickly change pipe and duct sizes and elevations while modeling. One firm says it is stuck on Revit 2026 until those tools return. This is the most recent item, and it's a user request, not an official change.
- **Electrical:** A Revit Ideas post says electrical designers need to replace connectors to a pipe connector just so they can model flex conduit, which is a frustration about conduit modeling. I found no sources on circuit limitations specifically.
- **Other tools:** A Graphisoft MEP Modeler thread, which is not Revit, complains that a change in duct size of as little as 50mm will produce a transition far larger than required.

Overall, the evidence is mostly anecdotal and older, with a few 2025–2026 items. For stronger coverage, search for Revit 2026/2027 MEP changes and electrical circuit topics separately.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:46.788Z

<details><summary>نتيجة أداة (7679 حرف)</summary>

```
Web search results for query: "Revit on Mac no native version request Autodesk idea; Civil 3D LandXML export import problems interoperability"

Links: [{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/13734286"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/12015332"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/6513047"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/m-p/6426997"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/7988221/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997/highlight/true/page/54"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997/page/27"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997/page/18"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/7392185/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/8591906/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997/page/26"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/13169320/highlight/true"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/8517843/highlight/true"},{"title":"Revit native to mac","url":"https://forums.autodesk.com/t5/revit-architecture-forum/revit-native-to-mac/m-p/9907827"},{"title":"Revit Architecture Forum","url":"https://forums.autodesk.com/t5/revit-architecture-forum/why-autodesk-does-not-have-revit-for-mac-version/td-p/8239359"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997/page/25"}]

Links: [{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2019/ENU/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/infraworks-forum/civil-3d-surface-import-problem/m-p/9508150"},{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2023/ENU/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2015/ENU/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2022/ENU/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"GUID 4D10ABA5 5EA0 41A8 BB61 C3F446CE7C6B","url":"https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2024/ENG/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"About Supported LandXML Data for Import and Export","url":"https://help.autodesk.com/cloudhelp/2021/ENG/Civil3D-UserGuide/files/GUID-4D10ABA5-5EA0-41A8-BB61-C3F446CE7C6B.htm"},{"title":"Showing results for","url":"https://forums.autodesk.com/t5/civil-3d-ideas/need-to-fix-a-serious-flaw/idi-p/9459790"},{"title":"communities.bentley.com","url":"https://communities.bentley.com/products/hydraulics___hydrology/w/hydraulics_and_hydrology__wiki/19268/elements-exported-to-landxml-not-correctly-importing-into-civil3d/revision/2"},{"title":"Trimble Business Center","url":"https://community.trimble.com/discussion/autocad-landxml-import-of-feature-lines-1"},{"title":"Převod jednotek u importovaných dat LandXML","url":"https://help.autodesk.com/cloudhelp/2015/CSY/Civil3D-UserGuide/files/GUID-471666D1-F265-40B3-A99B-74B8D90417D9.htm"},{"title":"41261700646419 LP360 Exported LandXML is Incomplete in Civil 3D","url":"https://support.lp360.com/hc/en-us/articles/41261700646419-LP360-Exported-LandXML-is-Incomplete-in-Civil-3D"},{"title":"Export / Import Surface XML file","url":"https://forums.autodesk.com/t5/civil-3d-forum/export-import-surface-xml-file/m-p/12876489"},{"title":"Import LandXML Files (.xml)","url":"https://help.fieldsystems.trimble.com/tbc/1009.htm"},{"title":"forums.autodesk.com","url":"https://forums.autodesk.com/t5/infraworks-forum/landxml-surface-problem-amp-frustration/td-p/6978405"},{"title":"Import a export ve formátu LandXML","url":"https://help.autodesk.com/cloudhelp/2019/CSY/Civil3D-UserGuide/files/GUID-767ED4FE-59EF-44F3-A90D-5CF0D8804375.htm"},{"title":"To Import LandXML Data","url":"https://help.autodesk.com/cloudhelp/2024/ENG/Civil3D-UserGuide/files/GUID-6CFC1A42-CA97-4263-B864-46A443DC487D.htm"}]

**Revit on Mac:** Autodesk has repeatedly declined a native macOS version. In one forum thread, the Revit product team said they are not planning on creating a Mac native version of Revit and have decided to prioritize the current Windows product. A more recent thread reports that a native Mac version is never going to happen, though one user noted that running Revit in Parallels has improved with MacOS 26 Tahoe over Sequoia. The idea has been posted for years, and the forum has merged many duplicates. Most of these results are community posts, not official roadmap statements.

**Civil 3D LandXML interoperability:** The results point to a few recurring problems:

- **Units mismatches:** One user found that an alignment exported to LandXML from a drawing set to US Survey feet opened with international units. Autodesk's response was that export and import work as expected when the units match across the source DWG, the LandXML export settings, the LandXML import settings, and the consuming DWG. The LandXML import command also handles conversion between the file's units and the current drawing units.
- **Surface import settings:** A LP360 export imported as only a fraction of the terrain, and the fix was to change the Surface Data value from full import to quick import. The vendor's note says the full import includes both points and faces, while the quick import only includes the points.
- **Version and duplicate-point errors:** In an InfraWorks case, re-importing the exported LandXML into Civil 3D 2018 produced errors about duplicate points and adjacent faces. The poster suspected the LandXML version, noting that the program switched automatically to LandXML version 1.1.
- **Feature line arcs:** A Trimble user reported that Civil 3D does not define the radius correctly for exported feature lines.
- **Survey database:** Autodesk's documentation warns that using the Import LandXML command from the File menu does not import survey data into the survey database.

Overall, the most common fixes in these threads are matching units across all settings, choosing full versus quick surface import, and checking the LandXML version. These are community reports and not an exhaustive or current list of known bugs, so check the Autodesk release notes for your Civil 3D version if you need to confirm a specific issue.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-23T07:57:47.345Z

<details><summary>نتيجة أداة (6439 حرف)</summary>

```
Web search results for query: "Rayon design browser 2D CAD collaborative architects funding; Hypar 2025 text-to-BIM status"

Links: [{"title":"Rayon example pages","url":"https://techcrunch.com/2023/09/27/rayon-is-a-collaborative-design-tool-for-architects-and-designers/amp/"},{"title":"Rayon example pages","url":"https://techcrunch.com/?p=2605647"},{"title":"paris based rayon raises e4 million to launch its collaborative architectural design tool","url":"https://www.eu-startups.com/2023/09/paris-based-rayon-raises-e4-million-to-launch-its-collaborative-architectural-design-tool/"},{"title":"rayon unveils norman foster backed design tool for developing architectural plans","url":"https://archinect.com:443/news/article/150377592/rayon-unveils-norman-foster-backed-design-tool-for-developing-architectural-plans"},{"title":"Rayon raises €4M for collaborative design tools in architecture and construction","url":"https://tech.eu/2023/09/27/rayon-raises-4m-for-its-collaborative-design-tools/"},{"title":"rayon builds the next generation collaborative space design software with 2m funding","url":"https://seedcamp.com/views/rayon-builds-the-next-generation-collaborative-space-design-software-with-2m-funding/"},{"title":"Today, we’re proud to announce that Rayon has raised a €10M Series A from","url":"https://fr.linkedin.com/in/marchelbling"},{"title":"announcing rayon s pre seed","url":"https://www.rayon.design/blog/announcing-rayon-s-pre-seed"},{"title":"rayon secures 4m","url":"https://siliconcanals.com/crowdfunding/rayon-secures-4m/"},{"title":"rayon seed round","url":"https://www.rayon.design/blog/rayon-seed-round"},{"title":"www.archdaily.com","url":"https://www.archdaily.com/1007480/rayon-a-design-software-revolutionizing-collaboration-for-efficient-project-development/{{url}}"},{"title":"Rayon: A Design Software Revolutionizing Collaboration for Efficient Project Development","url":"https://www.archdaily.com/1007480/rayon-a-design-software-revolutionizing-collaboration-for-efficient-project-development?ad_medium=gallery"},{"title":"paris based rayon draws up plans to expand its collaborative design software with fresh e1 9 million","url":"https://www.eu-startups.com/2022/06/paris-based-rayon-draws-up-plans-to-expand-its-collaborative-design-software-with-fresh-e1-9-million/"},{"title":"a peek into rayons ai future","url":"https://aecmag.com/cad/a-peek-into-rayons-ai-future/"},{"title":"rayon raises e10m for 3d and agentic ai","url":"https://aecmag.com/cad/rayon-raises-e10m-for-3d-and-agentic-ai/"}]

Links: [{"title":"hypar text to bim and beyond","url":"https://aecmag.com/ai/hypar-text-to-bim-and-beyond/"},{"title":"hypar text to bim and beyond","url":"https://aecmag.com/features/hypar-text-to-bim-and-beyond/"},{"title":"hypar 2 0","url":"https://aecmag.com/bim/hypar-2-0/"},{"title":"hypar 2 0","url":"https://aecmag.com/features/hypar-2-0/"},{"title":"AEC Magazine","url":"https://aecmag.com/tag/hypar/"},{"title":"metropolismag.com","url":"https://metropolismag.com/wp-json/wp/v2/metro_product/110723"},{"title":"AEC Magazine","url":"https://aecmag.com/tag/Hypar"},{"title":"Ai spotlight directory logo","url":"https://aidirectory.aecmag.com/entry/hypar/"},{"title":"Ai spotlight directory logo","url":"https://aidirectory.aecmag.com/?p=320"},{"title":"hypars big bet against schema","url":"https://aecmag.com/bim/hypars-big-bet-against-schema"},{"title":"Tech Startup Hypar Challenges the Traditional Design Pipeline","url":"https://enr.com/articles/56666-tech-startup-hypar-challenges-the-traditional-design-pipeline"},{"title":"Text2BIM: Generating Building Models Using a Large Language Model-based Multi-Agent Framework","url":"https://arxiv.org/html/2408.08054"},{"title":"arxiv.org","url":"https://arxiv.org/pdf/2408.08054v2.pdf"},{"title":"www.cbinsights.com","url":"https://www.cbinsights.com/company/hypar/customers"},{"title":"0% found this document useful (0 votes)","url":"https://www.scribd.com/document/773781821/Text-to-BIM"},{"title":"arxiv.org","url":"https://arxiv.org/html/2509.00543v1"},{"title":"Hypar’s Big Bet Against Schema","url":"https://www.pulse.bot/ai/news/hypars-big-bet-against-schema-3a747488-bb52-4f5c-8d69-a02a4e14343c/"},{"title":"Inside Hypar 2.0: The Future of Space Planning?","url":"https://bimpure.com/blog/inside-hypar-2-the-future-of-space-planning"}]

**Rayon**

Rayon is a browser-based tool for 2D collaboration. Its funding has grown across three rounds:

- **Pre-seed (2022):** Rayon's pre-seed round was led by Seedcamp, alongside Foundamental and 20VC. One report gives the amount as $2m, while another reports a raise of more than €1.9 million.
- **Seed (2023):** A €4 million seed round co-led by Northzone and existing investor Foundamental brought the total to €5.75 million. The money was for growing the team and launching the product.
- **Series A (€10M):** Rayon has raised €10 million in Series A funding led by Partech, with existing investors Northzone, Foundamental and Seedcamp also participating. The new funding will support further AI development, the addition of 3D and wider international reach. The results don't give a date for this round, so I can't confirm when it closed.

On the product side, it offers a browser-based tool that facilitates real-time collaboration on 2D floor plans, and users can import a variety of files, including images, PDF, and CAD documents (DWG, DXF).

**Hypar (2025 status)**

The results are mixed and don't give a clear 2025 status.

- A Hypar 2.0 release followed the earlier text-to-BIM work. An AEC Magazine feature dated February 2025 describes it as a cloud-based design tool that puts the spotlight on space planning.
- A December 2024 review says the text-to-BIM modeling function isn't available anymore.
- An AEC Magazine directory entry still describes Hypar as a BIM 2.0 platform that does rules-based generative design, producing BIM models from encoded building logic or natural language prompts. That listing may be outdated.
- Co-founder Ian Keough presented at NXT BLD 2025, which AEC Magazine called one of the best presentations there.

Taken together, text-to-BIM appears to have been dropped from the main product by late 2024, with the company focusing on space planning. I couldn't find a 2025 announcement confirming whether a text-to-BIM feature has returned.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-23T07:58:10.923Z

**أداة:** `Bash`

```json
{
 "command": "mkdir -p /Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research && ls /Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research",
 "description": "Create the research folder and list its contents"
}
```

### user · 2026-11-23T07:58:11.799Z

**نتيجة أداة:**
```
AGENT_CONTROL.md
AI_STACK_PLAN.md
BIM_ECOSYSTEM.md
COMPARE_SYSTEMS.md
FREE_AI_OPTIONS.md
MEDIA_SOURCES.md
NEWS_CRM_PLAN.md
OPENSOURCE_CDE_PLAN.md
README.md
REALITY_CAPTURE_PLAN.md
RENDER_STUDIO_PLAN.md
TOOLS_ECOSYSTEM.md
cmd_autocad.json
cmd_civil3d.json
cmd_navisworks.json
cmd_office.json
cmd_p6.json
cmd_plant3d.json
cmd_revit.json
coohom_tab_spec.md
gap_autocad.md
gap_civil3d.md
gap_navisworks.md
gap_p6.md
gap_plant3d.md
gap_revit.md
our_commands.json
sketchup_tab_spec.md
```

### assistant · 2026-11-23T07:59:31.626Z

**أداة:** `Write`

```json
{
 "file_path": "/Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md",
 "content": "# Market pain points: where users of AEC desktop tools are unhappy (2024 to 2026)\n\nResearch date: 2026-11-23. Method: 25 web searches; findings come from search-result summaries of the linked pages, not from reading every page in full. Forum posts and review sites are anecdotes, not measurements. Vendor-sponsored surveys are directional only. Anything marked **[unverified]** was not confirmed from a source. No prices are stated as fact; where a figure appears, it is \"as reported by\" the linked source and must be re-checked on the vendor's own page.\n\nReddit (r/Revit, r/AutoCAD, r/civil3d, r/gis, r/bim, r/projectmanagement) did not surface in the searches, so Reddit sentiment is not covered directly (see section 6).\n\n---\n\n## 1. Top 10 cross-cutting pain points\n\nRanked by how many product families and sources each one appeared in within this sample (a rough count, not a statistic).\n\n| # | Pain point | Seen in | Evidence |\n|---|---|---|---|\n| 1 | **Rising subscription cost, perpetual licences gone** | Autodesk, SketchUp, PlanSwift, Esri, P6, Coohom | Autodesk forum thread on an unexpected fee increase ([link](https://forums.autodesk.com/t5/installation-licensing-forum/unannounced-license-fee-increase/td-p/13771637)); SketchUp forum threads on yearly increases ([link](https://forums.sketchup.com/t/price-increases-another-increase-every-year/329950?page=2), [link](https://forums.sketchup.com/t/new-pricing-issue/335574)); PlanSwift reviewer on perpetual licences no longer supported ([Capterra](https://capterra.com/p/70808/PlanSwift/reviews/)); 2020 open letter on Revit cost of ownership ([AEC Magazine](https://aecmag.com/bim/letter-to-autodesk-aec-customers-demand-better-value/)) |\n| 2 | **Named-user licensing replaces shared/concurrent seats; metering added on top** | Autodesk, Esri | Esri concurrent-use retirement thread, with a county reporting a large renewal rise ([Esri Community](https://community.esri.com/t5/arcgis-pro-questions/arcgis-pro-concurrent-licensing-retiring/m-p/1509573)); Autodesk named-user transition ([Autodesk](https://www.autodesk.com/uk/campaigns/transition-to-named-user)); AEC Magazine on seats plus consumption ([link](https://aecmag.com/ai/autodesk-beyond-the-seat-the-meter/)); Schnitger on outcome pricing ([link](https://schnitgercorp.com/2025/10/08/autodesk-wants-you-to-pay-for-outcomes-not-just-access/)) |\n| 3 | **Slow or unstable on large models and datasets** | Revit, Civil 3D, Plant 3D, WebODM, Pix4D | Revit slow threads ([2024](https://forums.autodesk.com/t5/revit-structure-forum/revit-2024-slow/td-p/12517919), [multi-thread idea](https://forums.autodesk.com/t5/revit-ideas/multi-thread/idi-p/8260315/page/2)); Civil 3D G2 reviews on crashes and data loss ([G2](https://www.g2.com/products/civil-3d/reviews)); ODM memory failures ([ODM forum](https://community.opendronemap.org/t/what-is-your-biggest-pain-with-odm-opensfm/25791?page=2)); Pix4Dcloud failures on large image sets ([Pix4D community](https://community.pix4d.com/t/why-do-pix4dcloud-projects-fail-during-point-cloud-generation-on-large-image-sets/33771)) |\n| 4 | **Format lock-in and lossy exchange** (RVT versions, IFC, LandXML, XER/MPP) | Revit, Civil 3D, P6, Navisworks | Revit cannot save down ([Autodesk support](https://autodesk.com/support/technical/article/Backwards-compatibility-of-Revit-with-earlier-releases-of-the-software)); IFC export errors idea ([Revit Ideas](https://forums.autodesk.com/t5/revit-ideas/fix-ifc-export-errors/idc-p/13075799)); Revit-to-Archicad IFC thread ([Graphisoft](https://community.graphisoft.com/t5/Collaboration-with-other/Revit-IFC-to-Archicad-is-fundamentally-flawed/m-p/590036)); P6 to MS Project data loss ([Oracle docs](https://docs.oracle.com/cd/F25600_01/English/Mapping_and_Schema/ms_project_import_export_data_map_xml/97782.htm)) |\n| 5 | **Price goes up faster than the core product improves** | Revit, Civil 3D | 2020 open letter and Autodesk's admission of under-investment ([ENR](https://www.enr.com/articles/49825-autodesk-admits-its-underinvested-in-revit-development-over-100-firms-want-change)); \"two years on\" review ([AEC Magazine](https://aecmag.com/opinion/the-open-letter-two-years-on/)); Nordic letter, 2022 ([AEC Magazine](https://aecmag.com/bim/a-tale-of-two-open-letters/)); Civil 3D forum thread ([link](https://forums.autodesk.com/t5/civil-3d-forum/why-civil-3d-is-poor-software-aimed-only-at-autodesk-profits/td-p/12894406)) |\n| 6 | **Steep learning curve, dated interface** | P6, Coohom, Civil 3D | P6 reviews ([SelectHub](https://www.selecthub.com/p/ppm-software/primavera-p6/), [G2](https://g2.com/products/oracle-primavera/reviews_and_filters?page=3)); Coohom Trustpilot ([link](https://au.trustpilot.com/review/coohom.com)) |\n| 7 | **Web and free versions are cut-down** | AutoCAD Web, SketchUp for Web | AutoCAD Web LISP and display limits ([LISP help](https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/File-Management/AutoCAD_Web_Help_File_Management_Lisp_html.html), [visual differences](https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/File-Management/AutoCAD_Web_Help_VISUALDIFFERENCES_html.html)); SketchUp Free caps on new files and downloads ([forum](https://forums.sketchup.com/t/web-sketchup-free-version-start-limit-download-times/347759)) |\n| 8 | **Customer data ownership and portability in vendor clouds** | Autodesk | Nordic letter ([Archinect](https://www.archinect.com/news/article/150324438/nordic-architects-open-letter-reignites-scorching-autodesk-criticism)); AEC Magazine asks whether accumulated knowledge can leave with the customer ([link](https://aecmag.com/ai/autodesk-beyond-the-seat-the-meter/)) |\n| 9 | **Automation and calculation gaps that need manual work or add-ons** | Plant 3D, Revit MEP, AutoCAD Web | Plant 3D iso speed idea ([link](https://forums.autodesk.com/t5/autocad-plant-3d-p-id-ideas/faster-iso-creation/m-p/5995883)); slow Isogen data fill ([link](https://forums.autodesk.com/t5/autocad-plant-3d-forum/slow-isogen/td-p/8161726)); \"Massive overhaul of MEP\" idea ([link](https://forums.autodesk.com/t5/revit-ideas/massive-overhaul-of-mep/idi-p/13798653)) |\n| 10 | **No Mac or Linux** | Revit | Revit for Mac idea thread, open for years ([Revit Ideas](https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idi-p/6426997)) |\n\n---\n\n## 2. By product family\n\n### AutoCAD (desktop, Web, Mac)\n- **Complaints:** subscription cost and named-user terms (table rows 1, 2). AutoCAD Web cannot create or edit LISP routines and lacks many desktop commands; point clouds, PDF/DGN underlays and some xrefs do not display; drawings shared with you open view-only ([FAQ](https://help.autodesk.com/cloudhelp/ENU/AutoCAD-Web-Help/files/AutoCAD_Web_Help_FAQs_html.html)).\n- **Requested:** full scripting and full fidelity in the browser.\n- **Workflow to speed up:** open a DWG anywhere, make a small edit, send it back, without install or licence. **[inferred from the web limits; not a counted request]**\n- Mac feature gaps: **[unverified]**, no current source found.\n\n### Revit\n- **Complaints:** slow large models and belief that it leans on one core (row 3); no save to an earlier version, per Autodesk: \"does not have a feature to save to older version data formats\" ([support](https://autodesk.com/support/technical/article/Backwards-compatibility-of-Revit-with-earlier-releases-of-the-software)); IFC export loses properties and misplaces elements (row 4); years of under-investment (row 5); no Mac version, the product team saying it is \"not planning on creating a Mac native version of Revit\" ([thread](https://forums.autodesk.com/t5/revit-ideas/revit-for-mac/idc-p/12015332)).\n- **Requested:** save-as-previous-version ([idea](https://forums.autodesk.com/t5/revit-ideas/save-as-previous-version/m-p/6337733)), multi-threading, reliable IFC, Mac.\n- **Workflow to speed up:** everyday editing and sync on large linked models.\n\n### Revit MEP / HVAC\n- **Complaints:** sizing covers ducts and pipes but users report missing calculations (vents, refrigerant, gas, compressed air); automatic routing unreliable with custom fittings; conduit modelling is awkward ([thread](https://forums.autodesk.com/t5/revit-mep-forum/why-is-conduit-modeling-in-revit-so-terrible/m-p/9058015)). A recent idea reports quick size/elevation controls removed from the Options Bar in the newest release ([idea](https://forums.autodesk.com/t5/revit-ideas/piping-sizing-shortcut/m-p/14270605)). Evidence is mixed: some users say the built-in calculations are sufficient.\n- **Requested:** an MEP overhaul; fast in-place size and elevation changes.\n- **Workflow to speed up:** route, size and re-size long duct/pipe runs.\n\n### Civil 3D\n- **Complaints:** crashes with data loss and slowdowns on long corridors and big surfaces ([65 km road thread](https://forums.autodesk.com/t5/civil-3d-forum/poor-performance-on-65km-road-design/td-p/9055453)); performance depends on careful data-shortcut and xref setup ([AU class](https://www.autodesk.com/autodesk-university/class/Overcoming-the-Seven-Deadly-Sins-of-Civil-3D-Project-Performance-2026)); LandXML exchange trips on units, version and surface import mode ([LP360 note](https://support.lp360.com/hc/en-us/articles/41261700646419-LP360-Exported-LandXML-is-Incomplete-in-Civil-3D), [forum](https://forums.autodesk.com/t5/civil-3d-forum/export-import-surface-xml-file/m-p/12876489)). Autodesk claims corridor and surface speed-ups in 2025.1 ([blog](https://www.autodesk.com/blogs/aec/2024/08/19/whats-new-in-civil-3d-2025-1/)), a vendor claim.\n- **Requested:** bug fixes before features; stability.\n- **Workflow to speed up:** adjust an alignment or profile and see corridor and surface rebuild quickly.\n\n### Primavera P6 / Primavera Cloud\n- **Complaints:** expensive, hard for novices, dated reports that push users to export to spreadsheets for S-curves and histograms ([G2](https://g2.com/products/oracle-primavera/reviews_and_filters?page=3)); XER import failures, version errors and partial commits; lossy MS Project exchange ([Oracle import/export guide](https://docs.oracle.com/cd/F74771_01/English/admin/p6_pro_importing_exporting/p6_pro_importing_exporting.pdf)).\n- **Requested:** modern charts, easier onboarding.\n- **Workflow to speed up:** receive an XER, check it, and produce progress charts.\n- Primavera Cloud specific limits and AI features: **[unverified]**.\n\n### Navisworks\n- **Complaints:** weak evidence. Competitor content says clash data does not carry well over time ([Revizto blog](https://revizto.com/resources/blog/revizto-vs-navisworks-vs-acc-clash-data-future-planning)); G2 still rates its clash detection highly on a small sample ([G2](https://www.g2.com/compare/navisworks-vs-revizto)).\n- **Workflow to speed up:** triaging clash results into real issues **[unverified]**.\n\n### AutoCAD Plant 3D\n- **Complaints:** isometric generation is slow and still needs manual editing; Isogen title-block data fill is slow; high memory use ([G2](https://g2.com/products/autocad-plant-3d/reviews)). Overall ratings are positive.\n- **Requested:** faster iso creation, limited to a selected line.\n- **Workflow to speed up:** produce clean piping isometrics from the 3D model.\n\n### ArcGIS / QGIS\n- **Complaints (ArcGIS):** licence cost, loss of concurrent use, extras paid for in credits ([G2](https://g2.com/products/arcgis-pro/reviews?page=2), [Esri idea thread](https://community.esri.com/t5/arcgis-pro-ideas/feedback-on-arcgis-pro-licensing-changes-and/idc-p/1644797)).\n- **Complaints (QGIS):** thin evidence; some ArcGIS tools and map-series workflows are hard to rebuild, and enterprise geodatabase access is a gap, per a QGIS services vendor ([Lutra](https://www.lutraconsulting.co.uk/blogs/arcmap-is-dead-great-time-to-switch-to-qgis)).\n- **Workflow to speed up:** **[unverified]**.\n\n### SketchUp / Coohom\n- **SketchUp:** yearly price rises, no perpetual licence, the free web plan capped and without extensions (rows 1, 7; [Capterra](https://www.capterra.com/p/211798/SketchUp/pricing/)).\n- **Coohom:** confusing plans, surprise renewals, costs that jump when work must leave the platform; one reviewer distrusts its AI functions ([Trustpilot](https://au.trustpilot.com/review/coohom.com)). Capterra ratings are high ([link](https://www.capterra.com/p/192882/Coohom/reviews/)).\n- **Workflow to speed up:** model a room and export the result without hitting a paywall.\n\n### Quantity take-off (PlanSwift, CostX, Bluebeam)\n- **PlanSwift:** forced move to annual fees, lost take-off data between versions, raster-only measuring with no snapping to vector lines, no split screen ([G2](https://www.g2.com/products/PlanSwift/reviews)). No real-time collaboration listed, unlike Bluebeam ([G2 compare](https://www.g2.com/compare/bluebeam-vs-planswift)).\n- **CostX:** **[unverified]**, nothing found.\n- **Workflow to speed up:** measuring from PDFs, with assemblies reused across jobs.\n\n### Reality capture (ReCap, Pix4D, ODM)\n- **Pix4D:** pricing by quote for most tiers; cloud processing cost complaints ([thread](https://community.pix4d.com/t/pix4d-cloud-processing-costs-doubled/27426)).\n- **WebODM:** out-of-memory failures, no native chunking, slow ground-control step ([RAM thread](https://community.opendronemap.org/t/ram-requirements-and-cloud-based-processing/7199)).\n- **ReCap:** **[unverified]**, nothing found.\n- **Workflow to speed up:** large image sets processed without manual splitting or RAM tuning.\n\n---\n\n## 3. AI: what users want vs what vendors ship\n\n**What users say they want**\n- Automation of manual tasks: the top hope in AIA's 2025 study ([AIA](https://www.aia.org/about-aia/press/new-research-explores-perceptions-and-opportunities-artificial-intelligence)).\n- Help with documents and construction documentation rather than only concept images ([ArchDaily](https://www.archdaily.com/1040024/what-architects-expect-from-ai-tools-in-2026), [Bentley](https://www.bentley.com/blog/insights/ai-use-in-infrastructure-set-to-soar-as-firms-weigh-risks-and-returns/)).\n- Accuracy they can check, and data privacy: both named as leading barriers ([UpCodes report](https://marketing.up.codes/hubfs/Reports/UpCodes_State_of_AI_AEC_Report_2026.pdf)); many firms forbid vendors from training on their data ([Bentley](https://www.bentley.com/en/blog/bentley-survey-ai-data-security-aec-firms/)).\n- Adoption is still low ([ASCE](https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/12/18/architecture-engineering-construction-sector-slow-to-adapt-ai-survey-shows)).\n\n**What vendors ship**\n- Autodesk Assistant in Revit is a tech preview; actions are logged in the journal and labelled in Undo ([Autodesk blog](https://www.autodesk.com/blogs/aec/2026/04/22/autodesk-assistant-in-revit-tech-preview/), [help](https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-68D8FE6D-C5B0-4503-AE27-02C715BAC25B.htm)).\n- AI use is being metered: Fusion ties AI assists to monthly Flex tokens ([help](https://help.autodesk.com/cloudhelp/ENU/Fusion-CloudCredits/files/INCLUDED-QUOTA-TKNS.htm)), and AEC Magazine reports that automation still needs a licensed named-user seat ([link](https://aecmag.com/ai/autodesks-most-ambitious-ai-play-yet/)).\n- Challengers lead with agents: Motif ([AEC Magazine](https://aecmag.com/bim/inside-motif-the-agent-native-bim-platform/)), Snaptrude ([AEC Magazine](https://aecmag.com/bim/snaptrude-ai-conceptual-design-and-beyond/)), Rayon ([AEC Magazine](https://aecmag.com/cad/rayon-raises-e10m-for-3d-and-agentic-ai/)).\n\n**Gap:** users ask for checkable automation of boring production work on their own data; vendors ship chat assistants in preview, tied to seats and tokens. User reaction to Autodesk Assistant, Primavera Cloud AI, and ChatGPT/Claude use in AEC: **[unverified]**.\n\n---\n\n## 4. Challengers\n\n| Name | What it does well (one line) | Source |\n|---|---|---|\n| Snaptrude | Browser BIM for early design, the first of the \"BIM 2.0\" group; now pushing AI agents | [AEC Magazine](https://aecmag.com/bim/snaptrude-advances/) |\n| Arcol | Fast, collaborative conceptual design in the browser | [AEC Magazine](https://aecmag.com/bim/arcol-unleashed-bim-2-0/) |\n| Qonic | Browser model platform moving into authoring; the most construction-facing | [AEC Magazine](https://aecmag.com/bim/qonic-edges-towards-bim-authoring/) |\n| Motif | Browser-delivered BIM authoring built around agents | [AEC Magazine](https://aecmag.com/bim/motif-to-take-on-revit-exclusive-interview/) |\n| Hypar | Rules-based space planning in the cloud; text-to-BIM reportedly dropped **[status unverified]** | [AEC Magazine](https://aecmag.com/bim/hypar-2-0/), [BIM Pure](https://bimpure.com/blog/inside-hypar-2-the-future-of-space-planning) |\n| Speckle | Open-source data hub that moves model data between tools | [AEC Magazine](https://aecmag.com/collaboration/speckle-matures/) |\n| Rayon | Real-time collaborative 2D plans in the browser, with DWG/DXF/PDF import | [TechCrunch](https://techcrunch.com/2023/09/27/rayon-is-a-collaborative-design-tool-for-architects-and-designers/amp/) |\n| That Open Company | Open-source browser IFC toolkit (formerly IFC.js) and a platform to build BIM apps | [AEC Magazine](https://aecmag.com/software/that-open-company-raises-the-stakes/) |\n\nContext: [BIM 2.0: unfinished business](https://aecmag.com/bim/bim-2-0-unfinished-business/). Most challengers target architects and early design; civil, plant, scheduling and take-off in one browser workspace looks less contested **[inferred, not sourced]**.\n\n---\n\n## 5. Opportunities for T.O X\n\nEffort: S = days, M = weeks, L = months. Each ties to a row in section 1.\n\n1. **Never cap or lock the free tier's files** (row 1, 7). Publish a plain \"what is free, forever\" page. **S**\n2. **No account needed to open a file; share links are editable** (row 2, 7). **S**\n3. **XER pre-flight check** (row 4): open an XER in the browser, list version, missing calendars, broken relationships, before anyone imports it. **S**\n4. **Schedule charts straight from XER** (row 6): S-curve and resource histogram in one click, no spreadsheet step. **S**\n5. **LandXML checker** (row 4): show units, version, point and face counts, and warn on mismatch before import. **S**\n6. **IFC export health report** (row 4): after export, list elements dropped, moved, or without properties. **M**\n7. **Open formats as the saved format** (row 4, 8): projects stored as IFC/DXF/LandXML/XER plus plain JSON, with one-click full export. **M**\n8. **AI agent with a visible action log and preview before apply** (row 9, section 3): every agent step listed, undoable, and shown as a diff. **M**\n9. **Clear data promise** (row 8): user files are not used for training; say where files are stored. **S** (policy) plus **M** if local-first storage is added.\n10. **PDF take-off that snaps to vector lines** (row 9): read the PDF's vector geometry rather than treating it as an image; reusable assemblies. **M**\n11. **Extra MEP calculators** (row 9): vent, gas, compressed air, refrigerant line sizing as small tools the agent can run. Must be checked by an engineer before any claim of code compliance. **M**\n12. **Piping isometrics from a selected line** (row 9): generate one line's iso quickly with fewer manual fixes. **L**\n13. **Large-model loading that stays responsive** (row 3): streamed/tiled geometry and web workers; publish honest size limits. **L**\n14. **Photogrammetry job estimator** (row 3): before processing, estimate memory and split the job automatically; hand off to an ODM node. **M**\n15. **Works the same on Mac, Linux and tablets** (row 10): test and state supported browsers. **S**\n\n---\n\n## 6. Not verified / weak evidence\n\n- **Reddit** sentiment for all subreddits: none surfaced.\n- **buildingSMART forum and IFC5** discussions: none surfaced.\n- **AutoCAD for Mac** feature gaps; **ReCap Pro**; **CostX**; **Primavera Cloud** limits and AI: nothing found.\n- **Navisworks** complaints rest mainly on competitor marketing.\n- **QGIS** pain points rest on one vendor blog and scattered comments.\n- **User reaction to Autodesk Assistant** and **ChatGPT/Claude use in AEC**: no survey or forum evidence found.\n- **All prices and percentages** in linked sources (Autodesk fee rise, SketchUp increase, P6 and Coohom plan prices, survey figures) were not checked against vendor pages or full reports.\n- **Dates:** several forum threads cited are older than 2024 (Revit multi-thread, save-as-previous, Plant 3D iso, Civil 3D 65 km road); they show long-running requests, not new ones. The 2020 open letter's latest follow-up found is the 2022 Nordic letter; no 2024 to 2026 follow-up was found.\n- **Hypar** current product scope and whether **Autodesk removed multi-user licences everywhere**: not confirmed.\n- **Rankings in section 1** are a count across this small sample, not a market survey.\n- \"Workflow users most want faster\" lines are the author's reading of the complaints unless a request thread is linked.\n"
}
```

### assistant · 2026-11-23T07:59:32.526Z

**أداة:** `Bash`

```json
{
 "command": "wc -w /Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md",
 "description": "Count words in the new file"
}
```

### user · 2026-11-23T07:59:32.832Z

**نتيجة أداة:**
```
File created successfully at: /Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md (file state is current in your context — no need to Read it back)
```

### user · 2026-11-23T07:59:33.154Z

**نتيجة أداة:**
```
    2208 /Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md
```

### assistant · 2026-11-23T07:59:42.905Z

**أداة:** `SubagentHandback`

```json
{
 "message": "File written: `/Users/M7/Documents/Project_01_Sewage_Lift_Station/00_Source/work/site/docs/research/MARKET_PAIN_POINTS.md` (2,208 words, all 6 sections, 25 searches). No other file touched, no git.\n\nEvidence comes from search-result summaries of the linked pages, not from reading each page in full. The file says so at the top.\n\n**5 strongest opportunities**\n1. XER pre-flight check in the browser: list version, missing calendars and broken relationships before import (small).\n2. Schedule S-curve and resource histogram straight from XER, no spreadsheet step (small).\n3. AI agent with a visible action log, undo, and a diff preview before apply; this answers the accuracy barrier named in AEC surveys (medium).\n4. Open formats as the saved format (IFC/DXF/LandXML/XER plus JSON), with one-click full export and an IFC export health report (medium).\n5. Free tier with no file or download caps and no account needed to open a file; editable share links (small).\n\n**Top pain points found, by frequency in this sample**\n1. Rising subscription cost and loss of perpetual licences (Autodesk, SketchUp, PlanSwift, Esri, P6, Coohom).\n2. Named-user licensing replacing shared seats, with token/credit metering added on top.\n3. Slow or unstable on large models and datasets.\n4. Format lock-in: Revit cannot save to older versions, IFC export loses data, LandXML and XER/MPP exchange is lossy.\n\n**Could not verify**\n- Reddit sentiment: no subreddit results surfaced at all.\n- buildingSMART forum and IFC5 discussions: none surfaced.\n- Nothing found on AutoCAD for Mac gaps, ReCap Pro, CostX, or Primavera Cloud limits and AI.\n- User reaction to Autodesk Assistant, and ChatGPT/Claude use in AEC: no survey or forum evidence.\n- Navisworks complaints rest mainly on competitor (Revizto) marketing; QGIS pain points on one vendor blog.\n- No 2024 to 2026 follow-up to the 2020 open letter found; the latest is the 2022 Nordic letter.\n- All prices and percentages in the linked sources were not checked against vendor pages; the file states none as fact.\n- Several cited forum threads predate 2024 (Revit multi-thread, save-as-previous, Plant 3D iso, Civil 3D 65 km road).\n- Hypar's current scope is unclear; text-to-BIM reportedly dropped.\n- The section 1 ranking is a count over a small sample, not a market survey. \"Workflow users most want faster\" lines are my reading of the complaints unless a request thread is linked.\n\nSkipped: the chat-export step and ruflo memory/hook calls, because the brief said to touch no other file."
}
```

### user · 2026-11-23T07:59:43.245Z

**نتيجة أداة:**
```
{"success":true,"message":"Report delivered to your caller."}
```
