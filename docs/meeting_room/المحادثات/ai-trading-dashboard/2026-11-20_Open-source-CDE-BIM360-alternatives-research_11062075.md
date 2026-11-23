# Open-source CDE/BIM360 alternatives research

- المصدر: `ai-trading-dashboard`
- معرف الجلسة: `11062075-e726-4438-978c-43e58def372e`
- البداية: 2026-11-20T07:27:19.648Z — النهاية: 2026-11-20T07:31:26.741Z
- الرسائل: مستخدم 10 · مساعد 11 · أدوات 9
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** <system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); compare-systems = local_b019d3b5-49d1-45fc-9bdc-a0c7936ab7d6 (idle); s
- **آخر رد للمساعد:** I wrote `OPENSOURCE_CDE_PLAN.md` at `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/OPENSOURCE_CDE_PLAN.md`. I didn't edit any app source or commit anything.

The doc has the Arabic 6-line summary on top, then the candidate tables for BIM viewers, CDE and document control, and Gantt libraries. Licence, last-push date and repo size come from the GitHub API on 2026-11-20. It also has the competitor comparison, a data model sketch and the ranked top 10.

- **DHTMLX Gantt Community is now MIT, not GPL.** I read its `package.json`, README and LICENSE. Auto-scheduling, critical path and resource management are in the paid PRO edition, so keep our own critical-path calculation.
- **Embed (permissive licences, run in

---

## المحادثة الكاملة

### user · 2026-11-20T07:27:19.648Z

<system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); compare-systems = local_b019d3b5-49d1-45fc-9bdc-a0c7936ab7d6 (idle); security-review = local_04c5434d-6020-4eec-a519-264fc05532f6 (idle); tools-news-crm-plan = local_842a1b92-6cef-4d6b-b65c-600c9744587d (idle). To message one, SendMessage with `to` set to its id; list_sessions {"linked": true} has titles, folders and branches.
</system-reminder>

Background (from the session that started this one):
T.O X is a free browser engineering studio (R.X Revit-like, C.X AutoCAD-like, S.X Civil 3D-like, P.X Primavera-like, N.X Navisworks-like, HVAC, GIS, document control, agents). Built in /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad (site/ is the published tree; research docs go in site/docs/research/). Owner wants to reuse open source instead of writing code from zero, after checking it is good, safe, and matching. Rule: read-only research, never edit app source, never copy vendor code or artwork, label VERIFIED (source URL read) vs FROM MEMORY.

Task:
Write site/docs/research/OPENSOURCE_CDE_PLAN.md (Arabic 6-line summary on top, then English detail). Question: the owner wants a project-lifecycle hub like Autodesk BIM 360/ACC (owner / contractor / consultant roles; document control with RFI, IR, MOM folders; submittals, transmittals, issues, schedules, analysis, requests; start-from-scratch / import-and-edit / review-and-apply / ongoing follow-up). Find open-source or permissively licensed projects we can learn from or embed in a browser-only static page: BIM viewers and servers (That Open Company / web-ifc / ifc.js, BIMserver, xeokit, IfcOpenShell, BCF tools), CDE and document control (e.g. Speckle, OpenProject, Frappe/ERPNext Projects, Paperless-ngx, Nextcloud workflows), issue/RFI trackers, Gantt libs (frappe-gantt, dhtmlx GPL caveat), news/feeds readers. For each: licence (check GitHub API or the repo LICENSE), last commit date, size, runs in browser only?, what we would take (idea, schema, module), risks (licence copyleft, security, CORS), and a verdict: embed / learn-from / skip. Also compare with competitors' lifecycle models (BIM 360/ACC, Procore, Aconex, Trimble Connect, Bentley ProjectWise) in one table of strengths/weaknesses, labelled from memory unless a page was read. End with a ranked top-10 list of what to add to T.O X next and a data model sketch (roles, folders, document states, workflow steps). Do not edit any source file.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1

### assistant · 2026-11-20T07:27:26.708Z

**أداة:** `mcp__ccd_turn__update_plan`

```json
{
 "items": [
  {
   "content": "Read sibling notes and target folder",
   "status": "in_progress"
  },
  {
   "content": "Query GitHub API for repo facts",
   "status": "pending"
  },
  {
   "content": "Verify key licences/pages",
   "status": "pending"
  },
  {
   "content": "Write OPENSOURCE_CDE_PLAN.md",
   "status": "pending"
  }
 ],
 "scope": "first_task"
}
```

### user · 2026-11-20T07:27:27.156Z

**نتيجة أداة:**
```
Plan shown (4 steps).
```

### assistant · 2026-11-20T07:27:28.673Z

**أداة:** `Bash`

```json
{
 "command": "ls \"/Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1\" 2>&1 | head; ls /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research 2>&1 | head -50; gh auth status 2>&1 | head -3",
 "description": "List notes, research folder, gh auth"
}
```

### user · 2026-11-20T07:27:33.415Z

**نتيجة أداة:**
```
ME-GLY-01_texts_all.json
SLS01_dwg_texts.json
networks_data_register.md
networks_sewer_storm_world.json
networks_water_fire_world.json
profiles_sewer_storm_tables.json
AGENT_CONTROL.md
BIM_ECOSYSTEM.md
COMPARE_SYSTEMS.md
NEWS_CRM_PLAN.md
README.md
SECURITY_REVIEW.md
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
github.com
  ✓ Logged in to github.com account 686877M (keyring)
  - Active account: true
```

### assistant · 2026-11-20T07:27:37.180Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research; wc -l BIM_ECOSYSTEM.md NEWS_CRM_PLAN.md TOOLS_ECOSYSTEM.md; head -c 5000 BIM_ECOSYSTEM.md; echo ======; head -c 3000 NEWS_CRM_PLAN.md; echo =====; grep -n -i \"licen\\|VERIFIED\" TOOLS_ECOSYSTEM.md | head -30",
 "description": "Skim sibling research docs"
}
```

### user · 2026-11-20T07:27:38.254Z

<details><summary>نتيجة أداة (4712 حرف)</summary>

```
Exit code 1
     116 BIM_ECOSYSTEM.md
     219 NEWS_CRM_PLAN.md
     255 TOOLS_ECOSYSTEM.md
     590 total
# BIM ecosystem research for T.O X (2026-11-20)

## ملخص بالعربي (5 سطور)
1. Autodesk APS (ACC و Model Derivative و Viewer و Design Automation) ينفع يتكلم من صفحة بدون سيرفر بس بـ PKCE (تطبيق Single Page) وبالتوكن بتاع المستخدم؛ الأجزاء اللي بتتحاسب (ترجمة الموديل، Design Automation) محتاجة حساب وتكلفة.
2. المفتوح: IFC (ISO 16739-1:2024 = IFC4.3) + web-ifc (MPL-2.0، يشتغل في المتصفح WASM) هو أنسب حاجة تتعاد استخدامها؛ IfcOpenShell (LGPL) و Bonsai (GPL) على الجهاز مش في الصفحة.
3. معايير دورة الحياة: ISO 19650-2 ثمان مراحل (احتياج، دعوة مناقصة، رد، تعيين، تعبئة، إنتاج تعاوني، تسليم، إغلاق) + EIR/BEP/MIDP/TIDP + LOIN (ISO 7817-1:2024) بدل LOD.
4. مقترح لـ T.O X: 9 مراحل من الـ brief للتسليم، كل مرحلة فيها دور وكيل + فحص + بوابة موافقة بشرية، وأداة مفتوحة لكل خطوة (web-ifc, BCF, IDS, bSDD).
5. اللي ماتأكدش منه مكتوب في آخر الملف (أسعار APS الحالية، ترخيص xBIM وSpeckle بالتفصيل، محتوى مراحل 6-8 من ISO 19650-2).

## Evidence labels
- **VERIFIED** = the claim appeared in a search result text from the cited URL on 2026-11-20. Note: I read search-result excerpts, not always the full page. Treat VERIFIED as "source seen", re-check before contract/legal use.
- **MEMORY** = from my own knowledge, no URL read in this session. Re-check before relying on it.
- Nothing here copies vendor code or artwork.

---

## A. Autodesk Construction Cloud (ACC / BIM 360) and Autodesk Platform Services (APS)

APS was Forge, renamed 2021 (VERIFIED: https://aps.autodesk.com/node/2178). BIM 360 APIs and ACC APIs were being merged under the ACC naming (VERIFIED partly: RFI v2 consolidated with BIM 360 RFI, https://aps.autodesk.com/node/3723).

| Service | What it does | Auth | Limits / cost | Pure browser app? |
|---|---|---|---|---|
| Authentication (OAuth v2) | Gets 2-legged (app) or 3-legged (user) tokens | 3LO with PKCE for Single Page App type (VERIFIED: https://aps.autodesk.com/blog/getting-token-pkce-single-page-app, sample https://github.com/autodesk-platform-services/aps-pkce-webapp, MIT) | Authentication is listed as included, no per-call charge (VERIFIED, pricing profile via https://apis.io/plans/autodesk/autodesk-plans-pricing/, aggregator, weak) | YES for 3-legged with PKCE. 2-legged needs a client secret: never put it in the page (MEMORY, standard OAuth rule). |
| Data Management | Hubs, projects, folders, items, versions, OSS buckets (storage) | 3LO for ACC/BIM 360 hub data; 2LO for own buckets | Included in plan (aggregator, weak). 429 + retry-after when over limit (VERIFIED: https://aps.autodesk.com/en/docs/data/v2/developers_guide/rate-limiting/forge-rate-limits) | Probably yes with a 3LO token. CORS behaviour per endpoint NOT verified: test with a real call. |
| Model Derivative | Translates Revit/DWG/IFC/NWD etc. into viewable SVF2 and extracts properties/geometry | Token with data:read/write | Usage based, billed (VERIFIED: aggregator https://apis.io/plans/autodesk/autodesk-plans-pricing/) | Calls yes (if CORS ok); the cost goes to the signed-in user's APS app owner. |
| Viewer (JS) | Renders translated models in a page | Token | Viewer SDK calls included (aggregator, weak) | Yes, it is a JS library loaded from an Autodesk CDN. Licence: proprietary terms of service, MEMORY. It conflicts with the T.O X rule "no vendor code", so use only as an optional external link or iframe, not bundled. |
| Design Automation (now "Automation API") | Runs Revit/AutoCAD/Inventor/3ds Max headless in the cloud: WorkItem -> Activity -> Engine + AppBundles (VERIFIED: https://aps.autodesk.com/en/docs/design-automation/v3/developers_guide/field-guide) | 2LO or 3LO | 100 calls/min per app; quotas per engine; billed by usage (VERIFIED: https://aps.autodesk.com/en/docs/design-automation/v3/developers_guide/rate-limits/da-rate-limits). Renamed Automation API 2025-06-30 (VERIFIED: https://aps.autodesk.com/en/docs/design-automation/v3/change_history/changelog_v3/). | Needs a plugin (C# bundle) built on a desktop first. Calls from page are possible; the bundle is not. |
| Webhooks | Server pushes events (file versions, etc.) to a URL | 2LO or 3LO | Rate limits https://aps.autodesk.com/en/docs/webhooks/v1/developers_guide/rate-limits/forge-rate-limits (VERIFIED, numbers not read) | NO. A webhook needs a public HTTPS endpoint. A static page has none: use polling, or a tiny relay (n8n, serverless). |
| ACC Issues / RFIs / Submittals | Project-management data | 3LO (write depends on user permissions, VERIFIED for Submittals) | Submittals: 600 req/min per key and per user (VERIFIED: https://aps.autodesk.com/en/docs/acc/v1/overview/rate-limit(eval):1: ===== not found
```

</details>

### assistant · 2026-11-20T07:27:46.051Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7-Documents-ai-trading-dashboard/11062075-e726-4438-978c-43e58def372e/scratchpad && cat > repos.txt <<'EOF'\nThatOpen/engine_web-ifc\nThatOpen/engine_components\nThatOpen/engine_fragment\nbimspot/BIMserver-Web-Dashboard\nopensourceBIM/BIMserver\nxeokit/xeokit-sdk\nxeokit/xeokit-bim-viewer\nIfcOpenShell/IfcOpenShell\nbuildingSMART/BCF-XML\nbuildingSMART/IDS\nbuildingSMART/BCF-API\nspecklesystems/speckle-server\nopf/openproject\nfrappe/erpnext\nfrappe/frappe\nfrappe/gantt\npaperless-ngx/paperless-ngx\nnextcloud/server\nnextcloud/workflow_script\ndhtmlx/gantt\nmozilla/pdf.js\npocketbase/pocketbase\nplane-so/plane\nmakeplane/plane\nzulip/zulip\nFreshRSS/FreshRSS\nminiflux/v2\ngantt-task-react/gantt-task-react\nMaTeMaTuK/gantt-task-react\njsGanttImproved/jsgantt-improved\nmermaid-js/mermaid\nbpmn-io/bpmn-js\ncamunda/camunda\nfrappe/helpdesk\nifcjs/web-ifc-viewer\nIFCjs/web-ifc-three\nvasturiano/force-graph\njgraph/drawio\ntldraw/tldraw\nsqlite/sqlite\nsql-js/sql.js\nrhashimoto/wa-sqlite\nautomerge/automerge\nyjs/yjs\nEOF\nfor r in $(cat repos.txt); do gh api repos/$r --jq '[.full_name,(.license.spdx_id // \"NONE\"),.pushed_at[:10],.size,.stargazers_count,.archived,.default_branch]|@tsv' 2>/dev/null || echo \"$r\tERR\"; done",
 "description": "Query GitHub API for repo facts"
}
```

### user · 2026-11-20T07:28:31.766Z

<details><summary>نتيجة أداة (3091 حرف)</summary>

```
ThatOpen/engine_web-ifc	MPL-2.0	2026-11-20	283888	1101	false	main
ThatOpen/engine_components	MIT	2026-11-08	266670	749	false	main
ThatOpen/engine_fragment	MIT	2026-11-08	87483	232	false	main
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}bimspot/BIMserver-Web-Dashboard	ERR
opensourceBIM/BIMserver	AGPL-3.0	2026-03-13	632139	1775	false	master
xeokit/xeokit-sdk	AGPL-3.0	2026-11-18	2614968	966	false	master
xeokit/xeokit-bim-viewer	AGPL-3.0	2026-11-16	496980	576	false	master
IfcOpenShell/IfcOpenShell	LGPL-3.0	2026-11-19	386150	2976	false	v0.9.0
buildingSMART/BCF-XML	NOASSERTION	2024-10-21	18473	264	false	release_3_0
buildingSMART/IDS	NOASSERTION	2026-09-25	97741	333	false	development
buildingSMART/BCF-API	NOASSERTION	2025-06-16	2005	241	false	release_3_0
specklesystems/speckle-server	NOASSERTION	2026-11-12	418656	862	false	main
opf/openproject	GPL-3.0	2026-11-20	3201504	17567	false	dev
frappe/erpnext	GPL-3.0	2026-11-20	2065267	41463	false	develop
frappe/frappe	MIT	2026-11-20	1063824	11130	false	develop
frappe/gantt	MIT	2026-06-18	2709	6158	false	master
paperless-ngx/paperless-ngx	GPL-3.0	2026-11-20	238661	48368	false	dev
nextcloud/server	AGPL-3.0	2026-11-20	7605981	37573	false	master
nextcloud/workflow_script	AGPL-3.0	2026-11-14	1128	92	false	master
DHTMLX/gantt	MIT	2026-11-19	56041	1872	false	master
mozilla/pdf.js	Apache-2.0	2026-11-20	228640	54161	false	master
pocketbase/pocketbase	MIT	2026-10-26	147003	61578	true	master
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}plane-so/plane	ERR
makeplane/plane	AGPL-3.0	2026-11-18	220252	62834	false	preview
zulip/zulip	Apache-2.0	2026-11-19	665175	26272	false	main
FreshRSS/FreshRSS	AGPL-3.0	2026-11-20	37550	16634	false	edge
miniflux/v2	Apache-2.0	2026-11-19	39200	9954	false	main
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/repos#get-a-repository","status":"404"}gantt-task-react/gantt-task-react	ERR
MaTeMaTuK/gantt-task-react	MIT	2024-08-12	5632	1096	true	main
jsGanttImproved/jsgantt-improved	NOASSERTION	2026-04-14	5069	525	false	master
mermaid-js/mermaid	MIT	2026-11-20	284313	91171	false	develop
bpmn-io/bpmn-js	NOASSERTION	2026-11-19	17604	9740	false	develop
camunda/camunda	NONE	2026-11-20	1907064	4367	false	main
frappe/helpdesk	AGPL-3.0	2026-11-19	73798	3506	false	develop
ThatOpen/web-ifc-viewer	MIT	2023-09-29	53908	1039	false	master
ThatOpen/web-ifc-three	MIT	2024-04-17	40959	599	false	main
vasturiano/force-graph	MIT	2026-09-28	2772	2171	false	master
jgraph/drawio	Apache-2.0	2026-11-17	1869941	9485	false	dev
tldraw/tldraw	NOASSERTION	2026-11-19	1664501	51503	false	main
sqlite/sqlite	NOASSERTION	2026-11-20	591652	11073	false	master
sql-js/sql.js	NOASSERTION	2026-11-19	156919	13689	false	master
rhashimoto/wa-sqlite	MIT	2026-11-18	25287	1431	false	master
automerge/automerge	MIT	2026-11-17	135448	6744	false	main
yjs/yjs	NOASSERTION	2026-11-16	74020	23083	false	main
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T07:28:40.883Z

**أداة:** `Bash`

```json
{
 "command": "cd /tmp 2>/dev/null; for r in \"DHTMLX/gantt\" \"specklesystems/speckle-server\" \"buildingSMART/BCF-XML\" \"buildingSMART/IDS\" \"buildingSMART/BCF-API\" \"bpmn-io/bpmn-js\" \"jsGanttImproved/jsgantt-improved\" \"pocketbase/pocketbase\" \"xeokit/xeokit-sdk\" \"sql-js/sql.js\" \"yjs/yjs\"; do echo \"=== $r\"; gh api repos/$r/license --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | head -12 | cut -c1-160; done; echo; gh api repos/pocketbase/pocketbase --jq '.archived,.pushed_at,.description'; gh api repos/taigaio/taiga-back --jq '[.license.spdx_id,.pushed_at,.archived]|@tsv'; gh api repos/odoo/odoo --jq '[.license.spdx_id,.pushed_at]|@tsv'; gh api repos/redmine/redmine --jq '[.license.spdx_id,.pushed_at]|@tsv'",
 "description": "Read LICENSE heads of ambiguous repos"
}
```

### user · 2026-11-20T07:28:59.809Z

<details><summary>نتيجة أداة (6263 حرف)</summary>

```
=== DHTMLX/gantt
The MIT License (MIT)

Copyright (c) 2026 XB Software

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
=== specklesystems/speckle-server
Copyright (c) 2020-present AEC Systems.

Portions of this software are licensed as follows:

- All content residing under the "packages/server/modules/workspaces/" directory of this repository is licensed under "The Speckle Enterprise Edition (EE) licen
- All content residing under the "packages/server/modules/gatekeeper/" directory of this repository is licensed under "The Speckle Enterprise Edition (EE) licen
- Content outside of the above mentioned directories or restrictions above is available under the "Apache License" license as defined below.

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

=== buildingSMART/BCF-XML

(c) buildingSMART International Ltd. 

This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ 
=== buildingSMART/IDS
# LICENSE

(c) buildingSMART International Ltd.

This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit [http://creativecommons.org/licenses/by-nd/4.0/](http://creativecommons.org/licenses/by-nd/4.0/).
=== buildingSMART/BCF-API
(c) buildingSMART International Ltd. 

This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ 
=== bpmn-io/bpmn-js
Copyright (c) 2014-present Camunda Services GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

=== jsGanttImproved/jsgantt-improved
* Copyright (c) 2013-2018, Paul Geldart, Eduardo Rodrigues and Ricardo Cardoso.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of Paul Geldart, Eduardo Rodrigues and Ricardo Cardoso nor the names of its contributors
*       may be used to endorse or promote products derived from this software
*       without specific prior written permission.
=== pocketbase/pocketbase
The MIT License (MIT)
Copyright (c) 2022 - present, Gani Georgiev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

=== xeokit/xeokit-sdk
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU Affero General Public License is a free, copyleft license for
software and other kinds of works, specifically designed to ensure
cooperation with the community in the case of network server software.
=== sql-js/sql.js
MIT license
===========

Copyright (c) 2017 sql.js authors (see AUTHORS)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

=== yjs/yjs
The MIT License (MIT)

Copyright (c) 2023
  - Kevin Jahns <[REDACTED_EMAIL]>.
  - Chair of Computer Science 5 (Databases & Information Systems), RWTH Aachen University, Germany

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

true
2026-10-26T18:07:11Z
Open Source realtime backend in 1 file
MPL-2.0	2026-11-03T11:43:01Z	false
NOASSERTION	2026-11-20T07:27:52Z
NOASSERTION	2026-11-19T23:50:08Z
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T07:29:04.870Z

**أداة:** `Bash`

```json
{
 "command": "gh api repos/DHTMLX/gantt/contents/package.json --jq '.content' | base64 -d | grep -i -E '\"(license|version|name)\"'; gh api repos/DHTMLX/gantt/contents/README.md --jq '.content' | base64 -d | grep -i -n -E 'licen|gpl|mit|commercial' | head -15; gh api \"repos/DHTMLX/gantt/commits?path=LICENSE.txt&per_page=3\" --jq '.[]|[.commit.author.date[:10],.commit.message[:80]]|@tsv' 2>&1|head; gh api repos/DHTMLX/gantt/contents --jq '.[].name' | head -30; npm view dhtmlx-gantt license version 2>&1 | head -4; echo ---; npm view @thatopen/fragments license version 2>&1|head -3; npm view web-ifc license version 2>&1|head -3; npm view frappe-gantt license version 2>&1|head -3; gh api repos/xeokit/xeokit-sdk/contents/README.md --jq '.content'|base64 -d|grep -i -n -E 'licen|commercial'|head -8",
 "description": "Verify DHTMLX gantt licence claim and npm versions"
}
```

### user · 2026-11-20T07:29:23.286Z

<details><summary>نتيجة أداة (3032 حرف)</summary>

```
	"name": "dhtmlx-gantt",
	"version": "10.0.4",
	"license": "MIT",
3:[![npm: v.10.0.4](https://img.shields.io/badge/npm-v.10.0.4-blue.svg)](https://www.npmjs.com/package/dhtmlx-gantt) · [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md) · [![made by DHTMLX](https://img.shields.io/badge/made%20by-DHTMLX-blue)](https://dhtmlx.com/)
8:[Quick start](#quick-start) | [Build from source](#build-from-source) | [Features](#features) | [Community vs PRO](#community-vs-pro) | [Frameworks](#framework-integration) | [License](#license) | [Links](#useful-links)
14:![DHTMLX Gantt - Community (MIT) Edition](dhtmlx-gantt-mit.png)
16:This is the **Community Edition** of DHTMLX Gantt - distributed as the `dhtmlx-gantt` npm package under the **MIT License** and shipped as **readable source code** you can fork, modify, and rebuild. For advanced project management capabilities such as auto-scheduling, critical path, and resource management, see the [PRO edition](#community-vs-pro).
94:`codebase/` is build output (generated, not committed). After `npm run build` you can serve the files from `codebase/` directly via `<script>` tags, exactly like the npm package.
102:codebase/   build output (generated, not committed)
229:This edition is intended for schedule visualization and manual editing. Production project-management features - auto-scheduling, critical path, resource planning - are part of the commercial **PRO edition**.
231:| Feature | Community (MIT) | PRO |
293:## License
295:This Community Edition of DHTMLX Gantt is licensed under the **MIT License** - see [LICENSE.md](LICENSE.md).
297:You are free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of this software in any project, including closed-source and commercial applications, subject only to the MIT License terms. It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
320:The package also ships [AGENTS.md](AGENTS.md) with rules for AI agents (edition limits, common pitfalls). Point your assistant to `node_modules/dhtmlx-gantt/AGENTS.md`.
.github
.gitignore
.npmignore
AGENTS.md
CLAUDE.md
CONTRIBUTING.md
LICENSE.md
README.md
bower.json
dhtmlx-gantt-mit.png
dhtmlx_logo.svg
eslint.config.js
package-lock.json
package.json
samples
scripts
src
tsconfig.json
vite.config.js
whatsnew.md
license = 'MIT'
version = '10.0.4'
---
license = 'MIT'
version = '3.6.1'
license = 'MPL-2.0'
version = '0.0.80'
license = 'MIT'
version = '1.2.2'
18:* [License](https://xeokit.io/#pricing)
114:## 📜 Licensing & Commercial Use
116:xeokit SDK is licensed under **AGPLv3**, which requires that any modifications or integrations of xeokit SDK into a project must also be open-sourced under AGPLv3.
118:🪧 **Need a commercial license?** If your company requires xeokit SDK under a different licensing model for **proprietary or closed-source** applications, we offer **flexible commercial licensing options**.
```

</details>

### assistant · 2026-11-20T07:29:28.705Z

Status: GitHub licence and activity data collected (found DHTMLX Gantt Community is now MIT, not GPL). One last check on web-ifc, then I write the doc.

### assistant · 2026-11-20T07:29:30.191Z

**أداة:** `Bash`

```json
{
 "command": "gh api repos/ThatOpen/engine_web-ifc/readme --jq .content | base64 -d | grep -i -n -E 'browser|wasm|node|licen' | head -8; gh api repos/ThatOpen/engine_components/readme --jq .content | base64 -d | grep -i -n -E 'bcf|viewer|licen|fragment' | head -8; gh api repos/opf/openproject/contents/modules --jq '.[].name' | tr '\\n' ' '; echo; gh api repos/specklesystems/speckle-server/contents/packages --jq '.[].name' | tr '\\n' ' '",
 "description": "Check web-ifc, components, OpenProject modules"
}
```

### user · 2026-11-20T07:29:36.232Z

**نتيجة أداة:**
```
54:The current live build of web-ifc is available [here](https://thatopen.github.io/engine_web-ifc/build.zip). Using this allows you to test newest fixes before we make a release. If you wish to use this version then download the zip file and place the contents of the dist folder manually into your node_modules/web-ifc folder. I.e if you are using web-ifc-three then it will be node_modules/web-ifc-three/node_modules/web-ifc. Please note you must replace the javascript and the WASM.
60:1. Node v16 or later
71:## Building WASM module
75:The WASM library is built through emscripten, please see [the emscripten installation guide](https://emscripten.org/docs/getting_started/downloads.html) for information on how to set up emscripten. Afterwards `emsdk_env` needs to be in your path.
77:To build the WASM you also need CMAKE [see here](https://cmake.org/download/) and (on windows) MINGW [see here](https://sourceforge.net/projects/mingw/) - once installed (and in your path) run `npm run setup-mingw` to configure the environment for web-ifc.
79:### WASM library
85:Run `npm run build-release` to build a release version of the wasm binary and the accompanying web-ifc api. It will be placed in `./dist`.
96:emcmake cmake -S src/cpp -B src/cpp/build_wasm -DEMSCRIPTEN=true -DCMAKE_BUILD_TYPE=Release -DWEB_IFC_WASM_NATIVE_EXCEPTIONS=OFF
auth_plugins auth_saml avatars backlogs bim boards budgets calendar costs documents gantt github_integration gitlab_integration grids itsm job_status ldap_departments ldap_groups llm meeting my_page openid_connect overviews recaptcha reporting repositories resource_management squashtm_integration storages team_planner two_factor_authentication webhooks wikis xls_export 
fileimport-service frontend-2 ifc-import-service monitor-deployment objectloader objectloader2 objectsender preview-frontend preview-service server shared tailwind-theme ui-components-nuxt ui-components viewer-sandbox viewer webhook-service
```

### assistant · 2026-11-20T07:31:15.739Z

**أداة:** `Write`

```json
{
 "path": "/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/OPENSOURCE_CDE_PLAN.md",
 "content": "# Open-source plan for a T.O X project-lifecycle hub (CDE) — 2026-11-20\n\n## ملخص بالعربي (6 سطور)\n1. المطلوب \"مركز مشروع\" زي BIM 360/ACC: أدوار (مالك / مقاول / استشاري)، مجلدات (RFI, IR, MOM)، Submittals وTransmittals وIssues وجداول وطلبات، وأربع أوضاع: ابدأ من الصفر / استورد وعدّل / راجع وطبّق / متابعة مستمرة.\n2. اللي ينفع نحطه فعلاً جوه صفحة ثابتة: **web-ifc** (MPL-2.0، WASM) + **That Open components/fragments** (MIT) لعرض IFC، و**frappe-gantt** (MIT) أو **DHTMLX Gantt Community** (طلع MIT دلوقتي، مش GPL، اتأكدت من الـ README والـ package.json) للجداول.\n3. ممنوع نضمّن: **xeokit** و**BIMserver** و**OpenProject** و**Paperless-ngx** و**ERPNext** (AGPL/GPL = copyleft هيفرض ترخيصها على T.O X لو دمجنا الكود)؛ نتعلم منها الـ schema والـ workflow بس ونكتب بتاعنا.\n4. **BCF و IDS** مواصفات buildingSMART بترخيص CC BY-ND (مسموح نقرأها ونطبّقها، ممنوع نعدّل نصها وننشره)؛ **Speckle** سيرفر Apache-2.0 (ما عدا مجلدين Enterprise) بس محتاج Docker وقاعدة بيانات = مش browser-only، نتعلم منه.\n5. تحذير مهم: صفحة ثابتة مفيهاش سيرفر، فالأدوار (مالك/مقاول/استشاري) هتبقى **تنظيم شغل مش أمان**؛ المشاركة بين الأطراف بحزم Transmittal قابلة للتصدير/الاستيراد (ZIP + JSON موقّع بـ hash) لحد ما نضيف سيرفر اختياري.\n6. أول 10 حاجات للإضافة في آخر الملف (الأولى: نموذج بيانات المشروع + سجل المستندات + حالات ISO 19650 + محرك الـ workflow)؛ كل الأرقام من GitHub API يوم 2026-11-20، وكل ما هو \"من الذاكرة\" متعلّم صراحة.\n\n## Evidence labels and method\n- **VERIFIED-API** = read from `gh api repos/<owner>/<repo>` (licence SPDX, `pushed_at`, size, archived) on 2026-11-20.\n- **VERIFIED-FILE** = I read the LICENSE / README / package.json text of that repo on 2026-11-20 (what was read is named).\n- **MEMORY** = from my own knowledge, no page read. Re-check before relying on it.\n- `size` is the GitHub repo size in MB (git history + files), **not** the shipped bundle size.\n- \"NOASSERTION\" from the API means GitHub could not classify the licence; I read the file where noted.\n- Nothing here copies vendor code, schemas verbatim, or artwork. Read-only research; no app source was edited.\n- Overlap: Autodesk APS facts (VERIFIED) are in `BIM_ECOSYSTEM.md`; news/CRM in `NEWS_CRM_PLAN.md`. Not repeated.\n\n---\n\n## 1. The browser-only constraint (read this first)\nT.O X is a static site. That decides most verdicts:\n- **No server = no shared state.** Three parties (owner, contractor, consultant) cannot see one live register. Options, cheapest first: (a) **transmittal packages**: export a ZIP (files + `register.json` + SHA-256 per file), the other party imports it; works offline, auditable. (b) a shared folder / Git repo as the store (File System Access API or GitHub API with the user's own token). (c) optional sync server later (Supabase / own API); keep storage behind one adapter interface so this is a swap, not a rewrite.\n- **Roles are workflow labels, not security.** Anyone with the file can edit `localStorage`/IndexedDB. Do not call this \"access control\" in the UI until a server enforces it. State this in the product text.\n- **CORS:** feeds (RSS), most project APIs and Autodesk endpoints may not send CORS headers. News needs a tiny relay (see `NEWS_CRM_PLAN.md`). Autodesk calls are 3-legged PKCE only (VERIFIED in `BIM_ECOSYSTEM.md`).\n- **Licence rule for embedding:** MIT / BSD / Apache-2.0 = embed freely with notice. MPL-2.0 = file-level copyleft, fine if we ship the library unmodified and keep its licence. LGPL = ok as a separate dynamically-loaded component, awkward in a bundled static page. GPL / AGPL = embedding forces the whole T.O X combined work under that licence and publishing source; AGPL also triggers on network use. Only embed those if the owner decides T.O X itself is released under the same licence. That is a business decision, not mine.\n\n---\n\n## 2. Candidate table\n\n### 2a. BIM viewers, servers, formats\n| Project | Licence | Last push | Size | Browser-only? | What we would take | Risks | Verdict |\n|---|---|---|---|---|---|---|---|\n| **web-ifc** (ThatOpen/engine_web-ifc) | MPL-2.0 (VERIFIED-API; npm `web-ifc` 0.0.80, MPL-2.0 VERIFIED) | 2026-11-20 | 284 MB | **Yes**, C++ built to WASM with emscripten (VERIFIED-FILE README: build via emscripten). Also runs in Node. | Parse IFC in the page: spatial tree, properties, quantities, geometry. This is the IFC engine. | MPL file-level: ship unmodified, keep notice. WASM memory on big models (MEMORY: hundreds of MB IFC can fail on mobile). Version 0.0.x = API churn, pin the version. | **EMBED** |\n| **That Open engine_components** | MIT (VERIFIED-API) | 2026-11-08 | 267 MB | Yes (three.js based) | Ready-made loader, clipper, measurements, hider, **BCF topics** component (MEMORY: BCFTopics exists, not read). | Pulls three.js + fragments; keep to the pieces we need; semver churn. | **EMBED** (selective) |\n| **That Open engine_fragment** | MIT (VERIFIED-API; npm `@thatopen/fragments` 3.6.1 MIT) | 2026-11-08 | 87 MB | Yes | Compact binary model format so IFC is converted once and reloaded fast. | Format may change between majors; store original IFC alongside. | **EMBED** |\n| web-ifc-viewer / web-ifc-three | MIT | 2023-09-29 / 2024-04-17 | 54 / 41 MB | Yes | Nothing. Superseded by components. | Stale. | **SKIP** |\n| **xeokit-sdk / xeokit-bim-viewer** | **AGPL-3.0** (VERIFIED-FILE: LICENSE is AGPL text; README says AGPLv3 and sells a commercial licence) | 2026-11-18 / 2026-11-16 | 2615 / 497 MB | Yes (WebGL) | Learn: tree/storey/section-plane UX, XKT idea of pre-converted compact model. | AGPL forces source release of anything combined with it, including over a network. Commercial licence costs money. | **LEARN-FROM** (do not bundle) |\n| **BIMserver** (opensourceBIM) | AGPL-3.0 (VERIFIED-API) | 2026-03-13 | 632 MB | **No** (Java server) | Learn: revision model, IFC merge/diff, query-by-class API. | AGPL + server + Java; 8 months quiet. | **SKIP** (learn model only) |\n| **IfcOpenShell** | LGPL-3.0 (VERIFIED-API) | 2026-11-19 | 386 MB | Native C++/Python. A Pyodide/WASM route exists (MEMORY, not verified). | Schema-aware read/write/validate, IDS checking, IFC4.3 authoring, BCF python (`ifcopenshell.api`), **Bonsai** is GPL (separate). | LGPL fine as a separate service; in-page WASM build is large (tens of MB, MEMORY) and loads slowly. | **LEARN-FROM** now; optional local helper later for IDS validation |\n| **buildingSMART BCF-XML / BCF-API** | **CC BY-ND 4.0** (VERIFIED-FILE LICENSE) | 2024-10-21 / 2025-06-16 | 18 KB / 2 KB | Spec only | Issue file format: topics, comments, viewpoints (camera + clipping + component selection + snapshot), `.bcfzip`. Implement our own reader/writer. | ND = do not publish a modified copy of the spec text/schemas. Implementing the format is fine. Re-check ND wording with a lawyer before shipping a bundled XSD. | **LEARN-FROM / implement** |\n| **buildingSMART IDS** | CC BY-ND 4.0 (VERIFIED-FILE) | 2026-09-25 | 98 MB | Spec only | Information Delivery Spec: machine-readable \"what data each element must have\" checks, ties to LOIN. | Same ND note. A JS checker is ours to write; IfcOpenShell has a reference one. | **LEARN-FROM** |\n\n### 2b. CDE, document control, project management\n| Project | Licence | Last push | Size | Browser-only? | What we would take | Risks | Verdict |\n|---|---|---|---|---|---|---|---|\n| **Speckle** (speckle-server) | Apache-2.0 except `workspaces/` and `gatekeeper/` dirs under Speckle Enterprise licence (VERIFIED-FILE LICENSE head) | 2026-11-12 | 419 MB | **No**: server packages incl. `server`, `frontend-2`, `ifc-import-service`, `fileimport-service`, `preview-service`, `webhook-service` (VERIFIED-API dir listing). Postgres + Redis + S3-style storage needed (MEMORY). `viewer`, `objectloader`, `objectsender` are separate packages. | Learn: object-graph commits (stream/project → model → version), connectors, webhooks. Possibly embed `@speckle/viewer` later if the owner hosts a Speckle server. | EE dirs must be avoided; self-host effort; viewer needs a server to feed it. | **LEARN-FROM** |\n| **OpenProject** | GPL-3.0 (VERIFIED-API) | 2026-11-20 | 3.2 GB | No (Ruby on Rails). Has `bim`, `meeting`, `documents`, `gantt`, `backlogs`, `budgets`, `costs`, `storages`, `webhooks` modules (VERIFIED-API dir listing). | Learn: work-package types, statuses and **per-role workflow transitions**, meeting minutes (our MOM), BCF issue linkage, role/permission matrix. | GPL: cannot copy code into T.O X unless T.O X is GPL. Heavy install. | **LEARN-FROM** (best model for roles + workflows) |\n| **Frappe Framework** | MIT (VERIFIED-API) | 2026-11-20 | 1.1 GB | No (Python + MariaDB server) | Learn: DocType + workflow-state + permission-per-role pattern. | Server-only; huge. | **LEARN-FROM** |\n| **ERPNext (Projects)** | GPL-3.0 (VERIFIED-API) | 2026-11-20 | 2.1 GB | No | Learn: Project / Task / Timesheet / Issue field sets. | GPL. | **LEARN-FROM** (schema ideas only) |\n| **Paperless-ngx** | GPL-3.0 (VERIFIED-API) | 2026-11-20 | 239 MB | No (Django + OCR) | Learn: correspondent / document type / tag / storage path, **auto-match rules**, consume-folder idea, full-text index, audit log. | GPL. OCR stack is heavy. | **LEARN-FROM** |\n| **Nextcloud** (server, workflow engine) | AGPL-3.0 (VERIFIED-API) | 2026-11-20 | 7.6 GB | No (PHP server) | Learn: **Flow = event + conditions + action** rule builder; file tags; share links with expiry/password. | AGPL; server. | **LEARN-FROM** |\n| **Plane** (makeplane/plane) | AGPL-3.0 (VERIFIED-API; `plane-so/plane` path 404, repo moved) | 2026-11-18 | 220 MB | No | Learn: issue / cycle / module / state-group model (backlog, unstarted, started, completed, cancelled). | AGPL. | **LEARN-FROM** |\n| **Taiga back** | MPL-2.0 (VERIFIED-API) | 2026-11-03 | small | No (Django) | Learn: kanban/epics/user-story shape. | Not construction-specific. | **SKIP** |\n| **PocketBase** | MIT (VERIFIED-FILE) | 2026-10-26 | 147 MB | No (single Go binary, but a server) | Would be the easy optional sync backend (auth, collections, rules, realtime) behind our adapter. | GitHub API says **archived = true** (VERIFIED-API); I did not read why. Do not depend on an archived project without a fork plan. | **SKIP** until status is clear |\n| **Zulip, drawio, tldraw** | Apache-2.0 / Apache-2.0 / custom (NOASSERTION, MEMORY: watermark/commercial terms) | active | 665 / 1870 / 1665 MB | No / yes / yes | Not core. | tldraw licence is not permissive for us. | **SKIP** |\n\n### 2c. Gantt and schedule\n| Project | Licence | Last push | Size | Browser-only? | What we would take | Risks | Verdict |\n|---|---|---|---|---|---|---|---|\n| **frappe-gantt** | MIT (VERIFIED-API; npm 1.2.2 MIT) | 2026-06-18 | 2.7 MB | Yes, tiny SVG lib | Read-only-ish timeline with drag, dependencies arrows, view modes. Good for the hub's \"schedule\" tab. | No critical path, no resources, no baselines. We compute CPM ourselves (P.X already exists). | **EMBED** |\n| **DHTMLX Gantt (Community)** | **MIT** (VERIFIED-FILE: README says Community Edition, MIT; `package.json` `\"license\": \"MIT\"`, version 10.0.4; npm `dhtmlx-gantt` license = MIT) | 2026-11-19 | 56 MB | Yes | Mature gantt with editing; README states **auto-scheduling, critical path, resource management are PRO (commercial)**. | **The \"GPL caveat\" in the brief is outdated for the Community package**: it is MIT now (older standard edition was GPL-2.0, MEMORY). Still: PRO features need a paid licence; check the Community feature table before promising baselines. Keep our own CPM so no dependency on PRO. | **EMBED** as optional richer view; keep frappe-gantt as default |\n| jsgantt-improved | BSD-3-Clause (VERIFIED-FILE head) | 2026-04-14 | 5 MB | Yes | Alternative; old code style. | Smaller community. | **SKIP** (spare) |\n| gantt-task-react | MIT | 2024-08-12 | 5.6 MB | React only | — | **Archived** (VERIFIED-API). | **SKIP** |\n| mermaid | MIT | 2026-11-20 | 284 MB | Yes | Draw the workflow (state diagrams) in the docs/help tab; also has a `gantt` diagram type for quick views. | Not an editor. | **EMBED** (docs only) |\n| bpmn-js | LICENSE starts with MIT text, © Camunda (VERIFIED-FILE head only) | 2026-11-19 | 18 MB | Yes | Visual workflow editor. | MEMORY: the bpmn.io licence adds a clause that the logo/watermark must stay visible. I did not read the rest of the file. Overkill for a fixed ISO 19650 state machine. | **LEARN-FROM** (skip until we need user-drawn workflows) |\n\n### 2d. Viewer/utility pieces for the hub\n| Project | Licence | Last push | Browser-only? | Use | Verdict |\n|---|---|---|---|---|---|\n| **pdf.js** | Apache-2.0 | 2026-11-20 | Yes | Preview drawings/submittals/RFIs, text layer for search, annotate overlay. | **EMBED** |\n| **sql.js** / **wa-sqlite** | MIT (sql.js VERIFIED-FILE; wa-sqlite VERIFIED-API) | 2026-11-19 / 2026-11-18 | Yes (WASM SQLite; wa-sqlite can persist in OPFS) | Real queryable register in-page (filter, sort, join) instead of hand-rolled arrays. | **EMBED** (one of them) |\n| **Yjs / Automerge** | MIT (yjs VERIFIED-FILE; Automerge VERIFIED-API) | 2026-11-16 / 2026-11-17 | Yes | CRDT merge so two parties' registers can be merged without a server (WebRTC/file exchange). Optional phase 2. | **LEARN-FROM** now, embed in phase 2 |\n| **FreshRSS** / **Miniflux** | AGPL-3.0 / Apache-2.0 (VERIFIED-API) | 2026-11-20 / 2026-11-19 | No (servers) | Learn: OPML import, feed-item de-dup by GUID, folders, read/starred state. Miniflux (Apache) is a safe model to copy ideas from. In-browser we need a CORS relay. | **LEARN-FROM** |\n\n---\n\n## 3. Competitor lifecycle models (all MEMORY unless noted)\nAutodesk ACC facts that were read are in `BIM_ECOSYSTEM.md` (VERIFIED there: ACC APIs, RFIs, Submittals, rate limits). The table below is my recollection of product positioning, not a page read today.\n\n| Platform | Lifecycle model | Strengths | Weaknesses |\n|---|---|---|---|\n| **Autodesk BIM 360 / ACC** | Modules per phase: Docs (folders, versions, markups, sheets), Build (RFIs, submittals, issues, forms, assets), Design Collaboration (package sharing between disciplines), Takeoff, Cost; project roles + folder permissions; transmittals. | Tight with Revit/Civil 3D/Navisworks; versioning + markup; wide API (APS). | Per-seat cost; permission model complicated; BIM 360 being folded into ACC; vendor lock-in; weak on formal ISO 19650 naming/state out of the box (needs config). |\n| **Procore** | Project-management first: bid → pre-construction → build → closeout; RFIs, submittals, daily logs, drawings, budget, change events/orders, punch lists, inspections. | Best owner/GC cost + field tooling; huge marketplace; mobile first. | Models/BIM are secondary; priced per project value; less design-side coordination. |\n| **Aconex (Oracle)** | Document-centric **correspondence**: mail types, transmittals, formal workflows, audit trail, neutral to every party's system. | Contractual audit trail, large infrastructure/oil & gas use, multi-party neutrality (closest to formal \"transmittal\" culture). | Dated UI; model viewing weaker; heavy rollout. |\n| **Trimble Connect** | Open CDE: files, 3D model viewing, issues/BCF, ToDos, apps ecosystem; works with Tekla, SketchUp, Viewpoint. | Open formats (IFC/BCF) friendly; free tier; good on-site field with Trimble hardware. | Less formal document-control workflow; fewer finance modules. |\n| **Bentley ProjectWise** | Engineering-content CDE: managed-workspace, document check-in/out, formal **state and workflow** per document, civil/infrastructure (MicroStation, OpenRoads), iTwin for digital twins. | Strong infrastructure engineering, true document states + revision control, enterprise audit. | Complex/expensive; heavy admin; best only inside Bentley stack. |\n| **ISO 19650 (neutral reference)** | CDE zones: **WIP → Shared → Published → Archive**, with approval gates and a naming convention; 8 stages (see `BIM_ECOSYSTEM.md`). | Vendor-neutral; maps cleanly to any tool. | A standard, not a product; needs implementation. |\n\n**Gap T.O X can own:** free, offline-capable, Arabic-first, ISO 19650 states by default, transmittal packages as the sharing unit. We will not match their cloud, mobile or contract-grade audit; we say so.\n\n---\n\n## 4. Data model sketch (own implementation; ideas from ISO 19650, OpenProject workflows, Paperless metadata, Nextcloud flows, BCF)\n\n### 4.1 Roles (workflow labels; real enforcement needs a server)\n`owner` (client/employer), `consultant` (designer/supervisor/engineer of record), `contractor` (GC), `subcontractor`, `dctl` (document controller, can run transmittals), `viewer`.\nPer role, per folder: `read | upload | review | approve | admin`. Matrix lives in `project.permissions[]`. Defaults:\n- owner: approve on Contract / Approvals, read elsewhere.\n- consultant: review + approve on Design, Submittals, RFI replies, IRs; upload on Design.\n- contractor: upload on WIP/Shared contractor folders, raise RFI / IR / Submittal / Transmittal.\n- dctl: admin on registers, issues transmittals, cannot approve content.\n\n### 4.2 Entities\n```\nProject   { id, name, code, phases[], parties[], createdAt, mode }   // mode: scratch | import | review | followup\nParty     { id, projectId, org, role, people[] }\nFolder    { id, projectId, path, kind, namingTemplate, permissions[] }\nDocument  { id, projectId, folderId, number, title, discipline, type,\n            rev, state, versions[ {rev, fileHash, size, by, at, note} ],\n            tags[], linkedIds[], due, owner }\nWorkflow  { id, kind, states[], transitions[ {from,to,roles[],requires[]} ], sla }\nItem      { id, kind, number, title, state, ballInCourt, due, priority,\n            raisedBy, assignees[], docRefs[], modelRefs[], bcf?, thread[], history[] }\nTransmittal { id, no, from, to[], purpose, items[docId@rev], issuedAt, responseDue, ackBy[], packageHash }\nScheduleTask { id, wbs, name, start, finish, deps[], pct, baseline?, linkedItems[] }\nMeeting   { id, date, attendees[], agenda[], minutes[ {text, action?, owner, due} ], nextDate }\nAudit     { at, who, action, entityId, before?, after?, hash }   // append-only, hash-chained\n```\n\n### 4.3 Folder tree (default; ISO 19650-inspired + the owner's RFI / IR / MOM folders)\n```\n00 Project Info (contract, EIR, BEP, MIDP)\n01 WIP            (per party, private until shared)\n02 Shared         (coordinated, review allowed)\n03 Published      (approved for construction / for information)\n04 Archive        (superseded, read-only)\n10 Correspondence\n   RFI/            (Requests for Information)\n   IR/             (Inspection / Material Inspection Requests)\n   Submittals/     (shop drawings, materials, samples, method statements)\n   Transmittals/   (issued packages + receipts)\n   MOM/            (Minutes of Meeting)\n   Letters/\n20 Design (Arch / Str / MEP / Civil / Survey)  -> models (IFC), drawings (PDF/DWG), specs, BOQ\n30 Site (daily reports, photos, NCR, snag list)\n40 Schedule & Cost (baseline, updates, EOT claims, payment certificates)\n50 Closeout (as-built, O&M, warranties, handover)\n```\nNaming template (ISO 19650 style, editable): `PROJ-ORIG-VOL-LVL-TYPE-ROLE-CLASS-NUM_REV` e.g. `TOX-ABC-XX-00-DR-A-0001_P01`.\n\n### 4.4 Document states (CDE) and revision codes\n`WIP` (S0 / P-rev: private) → `Shared` (S1–S4: coordination, review, information) → `Published` (A-rev: approved) → `Archived` (superseded).\nReview outcome codes (colourable): **A** approved, **B** approved with comments, **C** revise and resubmit, **D** rejected / for information only. Suitability: S0 WIP, S1 coordination, S2 information, S3 review/comment, S4 approval, A/B construction.\n\n### 4.5 Workflows (state machines)\n- **RFI:** `Draft → Submitted → In Review (ballInCourt = consultant) → Answered → Closed` (branches: `Rejected`, `Reopened`, `Overdue` auto-flag at due date). Links: drawing, model element (BCF viewpoint), spec clause. Cost/time impact flags (Y/N) feed the claim log.\n- **IR (Inspection Request):** `Raised by contractor → Scheduled → Inspected → Approved | Approved with comments | Rejected → Re-inspect → Closed`. Attach checklist (ITP) and photos.\n- **Submittal:** `Draft → Submitted → Reviewed (A/B/C/D) → Resubmit (new rev) → Approved → Closed`; multi-reviewer sequence (consultant → PM → owner).\n- **Transmittal:** `Draft → Issued → Received/Acknowledged → Response due → Closed`; contains a frozen list of `doc@rev` + hash.\n- **Issue / clash (BCF-shaped):** `Open → Assigned → In Progress → Resolved → Verified → Closed`, with viewpoint (camera, clip, components) and comments; export as `.bcfzip`.\n- **MOM:** agenda → minutes → action items (each action becomes an Item with owner + due) → next meeting carries open actions.\n\n### 4.6 The four modes\n| Mode | What the hub does |\n|---|---|\n| **Start from scratch** | Wizard: project info, parties and roles, template folder tree + naming, workflow set, schedule skeleton. Output: empty project package. |\n| **Import and edit** | Import ZIP / folder / IFC / BCF / CSV register / MS Project XML (MEMORY: common export). Map columns to fields, detect duplicates by number+rev, show a diff, then commit. |\n| **Review and apply** | Reviewer queue by `ballInCourt`; side-by-side rev compare; stamp A/B/C/D; apply resolves linked Issues; produces a response transmittal. |\n| **Ongoing follow-up** | Dashboards: overdue RFIs/IRs/submittals, aging, ball-in-court per party, schedule slip, open MOM actions; weekly digest; audit trail view. |\n\n---\n\n## 5. Ranked top 10 for T.O X (what to add next)\n1. **Project + roles + folder + document-register model** (section 4) stored through one storage adapter (IndexedDB now). Own code; no dependency. Everything else hangs on it.\n2. **ISO 19650 document states + naming/revision rules + A/B/C/D review codes**, with validation of file names on upload. Own code; spec-driven.\n3. **Workflow engine** (data-driven transitions per role, due dates, ball-in-court, overdue flags) powering RFI, IR, Submittal, Issue. Learn from OpenProject / Frappe workflow, no copying.\n4. **Transmittal package export/import** (ZIP + `register.json` + SHA-256 + hash-chained audit) = the sharing mechanism between owner / contractor / consultant without a server.\n5. **IFC viewer embed**: web-ifc (MPL) + That Open components/fragments (MIT), with section planes and property panel; store converted fragments next to the original IFC.\n6. **BCF 2.1/3.0 issue import/export** with viewpoints, written by us from the spec (CC BY-ND: implement, do not republish the spec files).\n7. **Schedule tab**: frappe-gantt (MIT) bound to P.X data; optional DHTMLX Community (MIT) view; keep our CPM so no reliance on DHTMLX PRO.\n8. **pdf.js preview + markup layer** for drawings, submittals, RFI attachments; link markups to Items.\n9. **MOM module**: agenda/minutes/actions that spawn Items and carry forward open actions; print to PDF.\n10. **Register query layer**: sql.js or wa-sqlite for filter/sort/aggregate and CSV/Excel export; then, as phase 2, a feed/news panel (Miniflux-style de-dup, needs the CORS relay) and optional Yjs merge or sync server.\n\nNot recommended now: embedding xeokit, OpenProject, Paperless-ngx, ERPNext, BIMserver (copyleft or server-bound); building a BPMN editor; any \"secure roles\" claim without a server.\n\n---\n\n## 6. What I did not check\n- Full text of bpmn-js and tldraw licences; PocketBase archive reason; Speckle EE licence terms; Bonsai/Blender licence beyond GPL (MEMORY).\n- Actual bundle sizes and WASM load time of web-ifc / fragments in a browser (not run). Not tested with a real IFC.\n- Whether That Open's `BCFTopics` supports BCF 3.0 fully (MEMORY only).\n- Competitor features and pricing: memory only, no vendor page read today.\n- Legal reading of CC BY-ND for implementing BCF/IDS: my reading is \"implementing is allowed, republishing modified spec text is not\"; this is not legal advice.\n- GitHub \"last push\" can be a bot commit; it is a liveness hint, not proof of maintenance quality.\n"
}
```

### user · 2026-11-20T07:31:16.793Z

**نتيجة أداة:**
```
File created successfully at: /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/OPENSOURCE_CDE_PLAN.md (file state is current in your context — no need to Read it back)

Note: Write's parameters are named `file_path` and `content`. `path` was read as `file_path`.
```

### assistant · 2026-11-20T07:31:19.460Z

**أداة:** `mcp__ccd_turn__wrap_up`

```json
{
 "recap": "Wrote OPENSOURCE_CDE_PLAN.md in the T.O X scratchpad's site/docs/research/ folder: Arabic 6-line summary, candidate tables with licence/activity from the GitHub API, competitor table, data model, ranked top 10. No source edited, nothing committed."
}
```

### user · 2026-11-20T07:31:19.923Z

**نتيجة أداة:**
```
Nothing is pending, so the app draws no box; the recap is the session's status. Your closing message is your answer to the user: write it now, as the last thing you say this turn.
```

### assistant · 2026-11-20T07:31:26.741Z

I wrote `OPENSOURCE_CDE_PLAN.md` at `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/OPENSOURCE_CDE_PLAN.md`. I didn't edit any app source or commit anything.

The doc has the Arabic 6-line summary on top, then the candidate tables for BIM viewers, CDE and document control, and Gantt libraries. Licence, last-push date and repo size come from the GitHub API on 2026-11-20. It also has the competitor comparison, a data model sketch and the ranked top 10.

- **DHTMLX Gantt Community is now MIT, not GPL.** I read its `package.json`, README and LICENSE. Auto-scheduling, critical path and resource management are in the paid PRO edition, so keep our own critical-path calculation.
- **Embed (permissive licences, run in the browser):** web-ifc (MPL-2.0, WASM), That Open components and fragments (MIT), frappe-gantt (MIT), pdf.js (Apache-2.0).
- **Don't bundle (copyleft):** xeokit and BIMserver are AGPL, OpenProject, ERPNext and Paperless-ngx are GPL, and IfcOpenShell is LGPL. Bundling would force their licence onto T.O X. They are useful for learning schemas and workflows.
- **BCF and IDS are CC BY-ND specs.** Implementing the format is fine; republishing modified spec text is not.
- **Speckle needs a server.** It is Apache-2.0 apart from two Enterprise directories, and it needs Docker plus a database, so it can't run browser-only.
- **PocketBase is archived on GitHub.** I didn't read why, so I don't recommend depending on it.
- **Roles are labels, not security.** A static page has no server to enforce access, so I suggest sharing between parties through exportable transmittal packages (ZIP plus hashed JSON).

Not checked:
- The full bpmn-js and tldraw licences.
- Bundle size and WASM load time with a real IFC file.
- Any competitor product page. The competitor table is from memory and labelled that way.
- Whether the BCF-XML (CC BY-ND) implementation approach is legally sound — that's my reading, not legal advice.
