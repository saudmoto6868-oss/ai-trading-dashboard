# Competitor comparison for T.O X

- المصدر: `ai-trading-dashboard`
- معرف الجلسة: `38f040aa-93ba-4b4f-aa1d-5553cdcf4ae7`
- البداية: 2026-11-20T06:45:01.889Z — النهاية: 2026-11-20T06:48:06.673Z
- الرسائل: مستخدم 24 · مساعد 25 · أدوات 23
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** <system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); security-review = local_04c5434d-6020-4eec-a519-264fc05532f6 (working)
- **آخر رد للمساعد:** I wrote `COMPARE_SYSTEMS.md` at `.../scratchpad/site/docs/research/COMPARE_SYSTEMS.md`. It has the 6-line Arabic summary and 17 system blocks. After those come a T.O X versus the field table, the 15 ranked improvements, the feature matrix and 12 risks.

1. **Sources and labels:** every claim is tagged `[V]` (URL seen in a search excerpt), `[V-weak]` (aggregator only), `[M]` (memory) or `[R]` (read from the T.O X docs). I touched no source file.
2. **Mostly unverified:** all strengths and weaknesses and most feature-matrix cells are `[M]`. I read only search excerpts, never full vendor pages.
3. **Prices:** many conflict across sources (Archicad, Solibri, ProjectWise, TestFit). I found no price for ACC/Autodesk Build, Navisworks Manage (Autodesk's own page), Coohom or ArcGIS, so those are m

---

## المحادثة الكاملة

### user · 2026-11-20T06:45:01.889Z

<system-reminder>
Linked sessions now (status, not an instruction): civil-3d-revit-naviswork = local_1fda12b4-672e-433c-97a0-a2fa4978c236 (idle); bim-agents-research = local_001c0740-2903-4f11-be70-d9f61501ac1f (idle); ref-autocad-civil = local_5d0c48e2-9162-441f-b0c2-a4a42e271811 (idle); ref-revit-plant = local_c003c799-3536-4b10-92be-e69bf070d1d2 (idle); ref-p6-nav-sketch = local_332522b7-4772-4582-8dc5-c671dd22a80c (idle); security-review = local_04c5434d-6020-4eec-a519-264fc05532f6 (working). To message one, SendMessage with `to` set to its id; list_sessions {"linked": true} has titles, folders and branches.
</system-reminder>

Background (from the session that started this one):
T.O X is a free browser workspace (single HTML page, no server) combining ideas from Revit, AutoCAD, Civil 3D, Navisworks, Primavera P6, Plant 3D, SketchUp, Coohom, Excel/Word/PowerPoint, a GIS tab, a document-control (DC) module and AI agents that control the tools. The owner wants it compared against the well-known systems to see strengths, weaknesses, what can be exploited and improved: permissions, flexibility, speed, shortcuts, time saved, project workflow (owner, contractor, consultant), and full automation by agents. Rules: never invent values or features, mark VERIFIED (source URL seen) versus FROM MEMORY, no copying of vendor code or artwork. Another session edits the app source; you must NOT touch any source file.

Task:
Documentation task. Read `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/README.md`, `BIM_ECOSYSTEM.md` and the `gap_*.md` files in the same folder first. Then write `COMPARE_SYSTEMS.md` there. Compare T.O X (what exists: see `/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/MEETING_ROOM.md` for the build log) with: Autodesk Revit / ACC (BIM 360), Trimble Connect, Bentley (OpenBuildings, ProjectWise), Graphisoft Archicad / BIMcloud, Procore, Oracle Primavera Cloud / P6, Microsoft Project, Navisworks, Solibri, BlenderBIM/Bonsai, FreeCAD, Speckle, That Open Engine, QGIS / ArcGIS, Coohom, SketchUp, and AI-first design tools (Arcol, Snaptrude, Hypar, Autodesk Forma, Testfit). For each: 3 strengths, 3 weaknesses, pricing model, openness, what a browser-only free tool can realistically take from it, and what T.O X can do better (permissions and roles for owner / contractor / consultant, flexibility, speed, keyboard shortcuts, automation by agents, offline use, low cost). Finish with: a ranked list of 15 improvements for T.O X by value over effort, a feature matrix table (rows features, columns systems, cells yes / partial / no / unknown), and a list of risks. Cite a URL for every verified claim. Put a 6-line Arabic summary at the top. Report back in 5 lines.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1

### assistant · 2026-11-20T06:45:08.870Z

**أداة:** `mcp__ccd_turn__update_plan`

```json
{
 "items": [
  {
   "content": "Read research README, BIM_ECOSYSTEM, gap files",
   "status": "in_progress"
  },
  {
   "content": "Read MEETING_ROOM build log",
   "status": "pending"
  },
  {
   "content": "Verify key claims via web",
   "status": "pending"
  },
  {
   "content": "Write COMPARE_SYSTEMS.md",
   "status": "pending"
  },
  {
   "content": "Report back",
   "status": "pending"
  }
 ],
 "scope": "first_task"
}
```

### user · 2026-11-20T06:45:09.179Z

**نتيجة أداة:**
```
Plan shown (5 steps).
```

### assistant · 2026-11-20T06:45:10.980Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs && ls -la research; wc -c research/* MEETING_ROOM.md; ls \"/Users/M7/Library/Application Support/Claude/side-session-notes/local_7b9e3c52-4743-4f64-b7c1-c942011a52a1\""
}
```

### user · 2026-11-20T06:45:16.441Z

<details><summary>نتيجة أداة (2198 حرف)</summary>

```
total 976
drwxr-xr-x@ 21 M7  wheel     672 Nov 20 08:28 .
drwxr-xr-x@ 15 M7  wheel     480 Nov 20 08:20 ..
-rw-r--r--@  1 M7  wheel   19070 Nov 20 08:24 AGENT_CONTROL.md
-rw-r--r--@  1 M7  wheel   16777 Nov 20 08:24 BIM_ECOSYSTEM.md
-rw-r--r--@  1 M7  wheel     423 Nov 20 08:20 README.md
-rw-r--r--@  1 M7  wheel   40802 Nov 20 08:27 cmd_autocad.json
-rw-r--r--@  1 M7  wheel   28061 Nov 20 08:27 cmd_civil3d.json
-rw-r--r--@  1 M7  wheel   21312 Nov 20 08:25 cmd_navisworks.json
-rw-r--r--@  1 M7  wheel   13847 Nov 20 08:25 cmd_office.json
-rw-r--r--@  1 M7  wheel   24794 Nov 20 08:25 cmd_p6.json
-rw-r--r--@  1 M7  wheel   21828 Nov 20 08:27 cmd_plant3d.json
-rw-r--r--@  1 M7  wheel   58239 Nov 20 08:27 cmd_revit.json
-rw-r--r--@  1 M7  wheel    8484 Nov 20 08:28 coohom_tab_spec.md
-rw-r--r--@  1 M7  wheel    5806 Nov 20 08:28 gap_autocad.md
-rw-r--r--@  1 M7  wheel    5775 Nov 20 08:28 gap_civil3d.md
-rw-r--r--@  1 M7  wheel    7661 Nov 20 08:26 gap_navisworks.md
-rw-r--r--@  1 M7  wheel    7613 Nov 20 08:26 gap_p6.md
-rw-r--r--@  1 M7  wheel    4938 Nov 20 08:28 gap_plant3d.md
-rw-r--r--@  1 M7  wheel    8854 Nov 20 08:28 gap_revit.md
-rw-r--r--@  1 M7  wheel  149718 Nov 20 08:20 our_commands.json
-rw-r--r--@  1 M7  wheel    8690 Nov 20 08:28 sketchup_tab_spec.md
   19070 research/AGENT_CONTROL.md
   16777 research/BIM_ECOSYSTEM.md
     423 research/README.md
   40802 research/cmd_autocad.json
   28061 research/cmd_civil3d.json
   21312 research/cmd_navisworks.json
   13847 research/cmd_office.json
   24794 research/cmd_p6.json
   21828 research/cmd_plant3d.json
   58239 research/cmd_revit.json
    8484 research/coohom_tab_spec.md
    5806 research/gap_autocad.md
    5775 research/gap_civil3d.md
    7661 research/gap_navisworks.md
    7613 research/gap_p6.md
    4938 research/gap_plant3d.md
    8854 research/gap_revit.md
  149718 research/our_commands.json
    8690 research/sketchup_tab_spec.md
   44213 MEETING_ROOM.md
  496905 total
ME-GLY-01_texts_all.json
SLS01_dwg_texts.json
networks_data_register.md
networks_sewer_storm_world.json
networks_water_fire_world.json
profiles_sewer_storm_tables.json
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T06:45:19.561Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research && cat README.md BIM_ECOSYSTEM.md"
}
```

### assistant · 2026-11-20T06:45:20.674Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research && cat gap_revit.md gap_p6.md gap_navisworks.md"
}
```

### user · 2026-11-20T06:45:22.177Z

<details><summary>نتيجة أداة (24173 حرف)</summary>

```
# Gap: Revit vs T.O X `model` (Revit ribbon)

Legend: **[V]** = read on Autodesk help (URL given). **[M]** = from memory, not verified. Own wording, no vendor text.
Data in `cmd_revit.json` (277 keys; 12 verified, 219 from memory, 46 marked app-specific = not a Revit command).

## Verified sources (read)
- UI parts list (File tab, Quick Access, InfoCenter, Options Bar, Type Selector, Properties, Project Browser, Status Bar, View Control Bar, Drawing Area, Ribbon, tabs, contextual tab, panels): https://help.autodesk.com/cloudhelp/2024/ENU/Revit-GetStarted/files/GUID-3197A4ED-323F-4D32-91C0-BA79E794B806.htm
- Ribbon (expanded panels, dialog launcher, contextual tabs): .../Revit-GetStarted/files/GUID-1CA04013-04CE-4F55-9B0C-68FD7E7FF80B.htm
- Project Browser (hierarchy of views/schedules/sheets/groups/links/families; search box; Find in Project Browser): .../GUID-C8D3E5A6-02A5-43A9-AFFC-D49DD27398B1.htm
- Properties palette (Type Selector, instance vs type properties, view properties when nothing selected): .../GUID-A764EA7A-FE26-469B-857C-F3A70812FC34.htm
- Options Bar (below ribbon, shows tool/selection-dependent options): .../GUID-28BDE98C-E8A9-4C74-8ABC-9DABD13163D9.htm
- View Control Bar tool list: .../GUID-42872B9F-A4DE-472A-A88C-77879ACEC93E.htm
- Curtain elements: https://help.autodesk.com/cloudhelp/2021/ENU/Revit-ArchDesign/files/GUID-F20928C1-83F8-4CD0-870E-6F8F123A67C9.htm ; Window: .../2022/ENU/Revit-ArchDesign/files/GUID-3B7BAC64-6120-4372-A29E-95C4A1D853F5.htm
- Pipe (Systems tab, Plumbing & Piping panel; placeholder pipe): https://help.autodesk.com/cloudhelp/2024/ENU/Revit-MEPEng/files/GUID-EEB121ED-6C1F-4728-A615-B3AF36DD6A61.htm
- Panel Schedules (Analyze tab, Reports & Schedules panel): https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-3D2D0E77-ED17-4FBF-AAE4-CB9185A3F779.htm
- Systems Analysis (Analyze tab, Energy Optimization panel; EnergyPlus workflow): https://help.autodesk.com/cloudhelp/2020/ENU/Revit-Analyze/files/GUID-489D3898-82B1-4615-BDF2-DA1DC37A83BB.htm
- Not verified: the full tab/panel list of the Revit ribbon (no single help page found; pages differ per release).

## Real program frame
- Ribbon tabs [M]: File, Architecture, Structure, Steel, Precast, Systems, Insert, Annotate, Analyze, Massing & Site, Collaborate, View, Manage, Add-Ins, Modify; contextual tabs "Modify | <tool>" [V: contextual tab exists].
- Project Browser [V]: Views (by discipline), Legends, Schedules/Quantities, Sheets, Families, Groups, Revit Links.
- Properties palette [V]: Type Selector + instance parameters + Edit Type; shows active-view properties when nothing is selected.
- View Control Bar [V list]: Scale, Detail Level, Visual Style, Sun Path, Shadows, Rendering dialog (3D), Crop, Show Crop, Lock 3D view, Temporary Hide/Isolate, Reveal Hidden, Worksharing Display, Temporary View Properties, Analytical Model, Displacement Sets, Reveal Constraints.
- Options Bar [V]: per-tool options (e.g. wall height, chain, offset, tag options).

## Missing in ours, by priority
Browser notes: Three.js/web-ifc style scene; data model = JSON elements with `ifc_class`, `type`, parameters; IFC export via web-ifc.

### P1 Modelling
| Real feature | Gap | Browser idea | IFC / data |
|---|---|---|---|
| Wall types with layers, location line, join/cleanup [M] | single wall only | layer stack array, extrude per layer | IfcWall + IfcMaterialLayerSetUsage |
| Curtain System/Grid/Mullion [V] (11 of our 266 commands unbuilt) | not built | grid divisions on face, panel + frame meshes | IfcCurtainWall, IfcPlate, IfcMember |
| Stairs/Ramps by component, Railing on host [M] | basic | run + landing generator | IfcStair/IfcStairFlight, IfcRailing |
| Roof by footprint/extrusion, slope arrows [M] | simple roof | polygon + slope edges | IfcRoof, IfcSlab(ROOF) |
| Openings: By Face, Shaft, Vertical, Dormer [M] | unbuilt | CSG subtract (three-bvh-csg) | IfcOpeningElement |
| Model Group, Parts, In-Place Mass, Place Mass [M] | partly | group node; mass = extrude | IfcGroup, IfcBuildingElementProxy |
| Work plane set/show/ref plane/viewer [M] | unbuilt | plane gizmo and raycast to plane | n/a (editor state) |
| Structural: Brace, Truss, Beam System, rebar tools, fabric sheet [M] | unbuilt | parametric member generators | IfcMember, IfcReinforcingBar, IfcReinforcingMesh |
| Steel tab: connection, plate, bolt, anchor, weld, cope [M] | unbuilt | small parametric parts, no real calc | IfcDiscreteAccessory, IfcFastener, IfcMechanicalFastener |
| Linked models (Revit/IFC/CAD) as references [M] | CAD only | load IFC with web-ifc as locked layer | IfcProject (linked) |

### P2 Documentation
| Real feature | Gap | Browser idea | IFC / data |
|---|---|---|---|
| Dimensions: aligned/linear/angular/radial/diameter/arc length, spot elevation/coord/slope [M] | partly | SVG overlay with snap refs | annotation only (IfcAnnotation) |
| Tags: Tag by Category, Tag All, Material, Keynote [M] | unbuilt | label from param template per category | reads element parameters |
| Detail Line, Region, Detail Component, Revision Cloud, Repeating Detail, Insulation [M] | unbuilt | 2D layer per view in SVG | none (view-specific) |
| View Templates, Filters, Visibility/Graphics overrides [M] | unbuilt | per-view override table applied on render | none |
| Callout, Duplicate View, Legends, Scope Box [M] | unbuilt | view clone with cropped camera | none |
| Sheets: title block, revisions, guide grid, placed views [M] | basic sheet | SVG sheet with viewports | IfcDocumentInformation |
| Text: spelling, find/replace [M] | unbuilt | simple search over notes | none |

### P3 Quantities (Schedules)
| Real feature | Gap | Browser idea | IFC / data |
|---|---|---|---|
| Schedules/Quantities with fields, filter, sort, group, totals, calculated values [M] | ours has BOQ view | table over element params, group-by, sums, CSV | IfcElementQuantity, IfcQuantityArea/Volume/Length |
| Material takeoff, Room/Area schedules [M] | partly | volume x layer; room areas from boundaries | IfcSpace quantities |
| Panel Schedules [V] | unbuilt | circuit table per panel from wire/circuit data | IfcElectricDistributionBoard, IfcElectricFlowStorage... (data in Pset) |
| Project/Shared/Global parameters [M] | project info only | parameter definitions JSON bound to categories | IfcPropertySet |

### P4 MEP systems
| Real feature | Gap | Browser idea | IFC / data |
|---|---|---|---|
| Duct/Pipe/Flex/Placeholder with routing preferences [V pipe] | almost all unbuilt (* in list) | polyline + auto fittings; type with size/slope | IfcDuctSegment/IfcPipeSegment + fittings |
| Fittings, accessories, air terminals, equipment with connectors [M] | unbuilt | families with connector points; snap | IfcDuctFitting, IfcPipeFitting, IfcAirTerminal |
| Electrical: panels, devices, lighting, cable tray, conduit, wire, circuits [M] | unbuilt | devices + circuit graph | IfcElectricDistributionBoard, IfcLightFixture, IfcCableCarrierSegment |
| Plumbing fixtures, sprinklers [M] | unbuilt | families with pipe connectors | IfcSanitaryTerminal, IfcFireSuppressionTerminal |
| Systems browser (assign/rename systems, system graphics) [M] | colour toggle only | systems table + colour filter | IfcSystem / IfcDistributionSystem |
| Spaces/zones, loads, Systems Analysis [V] | partial | simple load estimate, no EnergyPlus | IfcSpace, IfcZone, Pset_SpaceThermalLoad |
| Check systems, Interference Check, pressure loss reports [M] | partial | graph connectivity check; AABB clash | none |
| Duct/Pipe sizing methods [M] | partial | friction/velocity formulas | Pset only |

### P5 Rest
Phasing, Design Options, Worksets, Copy/Monitor, Manage Links, Dynamo (not feasible fully; offer JS scripting), Massing & Site tools (Toposurface etc.), Point Cloud/Decal, View Control Bar items (Sun Path, Shadows, Crop, Temporary Hide/Isolate, Reveal Hidden), Options Bar per-tool.

## Ours but not in Revit (46 entries tagged app-specific)
Examples: Agent hub, Telegram bot, Pulse and handover, Project cycle, Calendar, Ghost concrete, Water, Ground, Levels toggle, Structural/MEP/Quality review, Handover, Live session, Activity log, Search everywhere, Share, Saved projects, Record video, Screenshot, X-ray, BOQ CSV/XLSX, OBJ and SVG export, Station parameters, Plan to CAD. Keep them but label as "T.O X extra" so users do not expect them in real Revit.

## Naming mismatches worth fixing
- "Check" (Analytical Model) is not a Revit command name (Revit: consistency checks).
- Revit visual styles: Wireframe, Hidden Line, Shaded, Consistent Colors, Realistic [M]; ours has Wireframe, Shaded, X-ray.
- Export in real Revit: File > Export (IFC, CAD formats, PDF, FBX, gbXML) [M]; OBJ/SVG are not native.
- Duplicate names in ours (Wall x3, Cut x3, Copy x2, ...) are different tools; see keys with panel suffix in `cmd_revit.json`.
# Gap: Primavera P6 Professional vs our `sched` tab

Legend: **[V]** verified from page read (URL below). **[M]** from memory, not verified. Own wording, no vendor text copied.

Pages read:
- [V1] https://docs.oracle.com/cd/F74771_01/client_help//en_US/activities_window.htm (Activities window, P6 Professional help v23)
- [V2] https://docs.oracle.com/cd/F74771_01/English/User_Guides/p6_pro_user/the_resource_usage_profile.htm (Resource Usage Profile)
- Search results only (titles/snippets, pages not fully read): Oracle P6 Professional User Guide PDFs v20/v21/v25 under docs.oracle.com/cd/*/English/User_Guides/p6_pro_user/p6_pro_user.pdf.

## 1. What real P6 Professional has

### Window structure
- Main windows [M]: Projects, WBS, Activities, Resource Assignments, Tracking, Reports, Resources, Roles, Calendars, Cost accounts, Codes etc. Each is a tab; Activities stays open until projects close [V1].
- Activities window [V1]: **top layout** + **bottom layout**. Top: Activity Table, Gantt Chart, Activity Network. Bottom: Activity Details, Activity Usage Profile, Resource Usage Profile, Activity Usage Spreadsheet, Resource Usage Spreadsheet, Trace Logic [V1/V2 say Resource Usage Profile only in bottom, Network only in top].
- Layout Options bar + View menu + Top/Bottom Layout toolbars switch layouts [V1].
- Compare view: a second activity view beside the first to compare projects or baselines, each layout independent [V1].
- Edit toolbar/menu: add, delete, cut, copy, paste, link, renumber, dissolve, undo [V1]. Assign toolbar: resources, roles, activity codes, predecessors, successors, step templates [V1].
- Right-click Expand All / Collapse All [V1]. "Hide If Empty" in Group and Sort for empty WBS bands [V1].

### Concepts the guide lists as first-class [V1]
Activity codes and values, activity dates, steps and step templates, activity types, relationships, baselines, calendars, earned value, expenses, future period bucket planning, grouping (by field / WBS path / hierarchy), leveling, progress spotlight, resources, roles, risks, scheduling, sorting, store period performance, summarizing, updating progress, WBS, work products and documents. Past period actuals, notebooks, constraints, durations/percent-complete types, milestones, activity owner (EPPM connected only).

### Resource Usage Profile [V2]
Histogram of units or cost for resources or roles, for one project or all projects (total allocation). Options: cost vs quantity, timescale, past-period actual vs actual-to-date, stacked histogram (colors/patterns), cumulative curves, "banana" curve early vs late, overload identification, average line, save/share profile. Uses resource curves and Usage Spreadsheet manual values.

### Menus [M]
File, Edit, View, Project, Enterprise, Tools, Admin, Help. Tools: Schedule (F9), Level Resources, Apply Actuals, Update Progress, Summarize, Store Period Performance, Claim Digger, Global Change, Reports, Tracking, Publish, Check-in/out, Schedule Check (newer). Enterprise: EPS, OBS, Resources, Roles, Calendars, Cost accounts, Codes, User Defined Fields.

## 2. Our `sched` tab today (from our_commands.json, 92 rows)
Have (built*): New, Open, Save, Projects, Print, Export XER/MS Project XML/XLSX/CSV, Undo/Redo, Find, Activities (Gantt), Timeline dock, 4D schedule, Zoom x3, WBS, Activities, Work Products and Documents, Expenses, Issues, Risks, Maintain Baselines, Project details, Calendar, Calendars, Schedule (F9), Update Progress, Scenarios and risk, Claim Digger, Check Schedule, Follow-up reports, Reports, Report Wizard, Tracking, Publish, Video of 4D, Users.
Listed but not built: everything else (Import XER/XLSX, Cut/Copy/Paste/Add/Delete/Dissolve/Renumber, all Assign items, Activity Network, Usage Spreadsheet, Resource Usage Profile, Columns/Bars/Timescale/Filters/Group and Sort/Bottom Layout/Progress Line, Resource Assignments, Thresholds, Assign Baselines, EPS/OBS/Resources/Roles/Cost Accounts/Codes/UDF, Level Resources, Apply Actuals, Recalculate Costs, Summarize, Store Period Performance, Global Change, admin items).

## 3. Gaps, prioritised (P0 = owner's complaint "missing details")

| Pri | Gap | Why | Browser build |
|---|---|---|---|
| P0 | **Top/bottom layout + Activity Details panel** (General, Status, Relationships, Resources, Codes, Steps, Notebook tabs) | Core P6 feel [V1] | Split pane; bottom panel is tabs bound to selected row |
| P0 | **Predecessor/successor editing** with FS/SS/FF/SF + lag, in table and by dragging in Gantt | Without logic no CPM | Relationship table + drag handle on bars; validate cycles |
| P0 | **Columns, Group and Sort, Filters** dialogs + saved layouts | Daily P6 use [V1] | Column picker, multi-key sort, group by WBS/code/any field, filter builder (field/op/value, AND/OR), localStorage layouts |
| P0 | **Activity types, duration types, percent-complete types, constraints, milestones** | Needed for correct dates [V1] | Fields on activity; engine honours them in F9 |
| P0 | **Calendars** (global/project/resource, holidays, exceptions) assigned per activity | Dates wrong otherwise | Calendar editor + work-day arithmetic in engine |
| P1 | Add/Delete/Dissolve/Cut/Copy/Paste/Renumber IDs | Basic editing [V1] | Row ops; Dissolve = reconnect preds to succs |
| P1 | **Resources, Roles, Assignments** + Resource Usage Profile/Spreadsheet | Histogram, overload [V2] | Resource dictionary, assignments, canvas histogram + cumulative curve, stacked mode, resource curves |
| P1 | **Baselines** (maintain, assign primary/secondary) + baseline bars in Gantt | Variance reporting | Snapshot activities into baseline sets; extra bars |
| P1 | **Activity Network** (boxes + lines) | Logic review [V1] | SVG/canvas auto layout by WBS or time; drag-create links |
| P1 | Progress: actual dates, % complete, remaining duration, Progress Line, progress spotlight | Update cycle [V1] | Data date; line drawn on Gantt |
| P1 | Level Resources, Apply Actuals, Summarize, Store Period Performance | Tools menu [V1] | Leveling = priority-based shift; summarize = roll-up to WBS |
| P2 | Steps and step templates, expenses detail, thresholds/issues, notebook topics | Detail fidelity [V1] | Child tables |
| P2 | Codes: activity/project codes, UDFs, EPS/OBS, cost accounts | Enterprise data [M] | Generic code-type tables used by group/filter |
| P2 | Compare view (project vs baseline) | [V1] | Second Gantt pane |
| P2 | Import XER/XLSX; Global Change; Report Wizard fields | Interop | XER text parser (tables TASK, TASKPRED, PROJWBS, CALENDAR); rule-based bulk edit |
| P3 | Trace Logic, Admin pages, security profiles, currencies, financial periods | Rarely used offline | Later |

## 4. How to build core features in a browser (concise)
- **CPM engine**: forward/backward pass on a DAG, 4 relationship types + lag in calendar units, constraints (start-on-or-after, finish-on-or-before, mandatory), total/free float, critical = TF ≤ 0. Calendar math is the hard part; unit-test against hand-computed XER sample.
- **Gantt**: canvas/SVG, timescale zoom levels, bar types configurable (current, baseline, critical, summary, milestone), relationship lines.
- **Table**: virtualised rows, editable cells, column resize/reorder, WBS tree with collapse.
- **Data model**: projects → WBS → activities → relationships / assignments / steps / codes; export XER by table mapping.

## 5. Not verified
Exact menu order and toolbar icons, keyboard shortcuts other than F9, Schedule Check availability by version, XER table list, P6 EPPM web differences. Filters/baselines/calendars pages not opened (only listed in V1 index).
# Gap: Navisworks vs our `coord` tab

Legend: **[V]** verified from a page read. **[M]** from memory. Own wording.

Pages read:
- [V1] https://help.autodesk.com/cloudhelp/2022/ENU/Navisworks/files/GUID-3539A344-FD91-4F2C-8744-2A5A9828B4C1.htm (Reference for Dockable Windows)
- Search-result snippets only (pages not fully read): Dockable Windows 2014; Default Keyboard Shortcuts 2022 (GUID-E5041421-...); Overview of Clash Detective 2014; Use TimeLiner and Animator for Time-Based Soft Clashing 2024; Link to a TimeLiner schedule for soft clashing 2014.

## 1. What real Navisworks has

### Dockable windows [V1]
- **Main Tools**: Clash Detective (Manage only), TimeLiner, TimeLiner Playback, Autodesk Rendering (when rendering system on), Animator, Scripter, Appearance Profiler.
- **Review**: Selection Tree, Sets, Find Items, Selection Inspector, Properties, Comments, Find Comments, Measure Tools, Set Scale by Measurement.
- **Quantification**: Quantification Workbook, Item Catalog, Resource Catalog.
- **Viewpoint**: Saved Viewpoints, Tilt, Plan View, Section View, Section Plane Settings (3D workspace).
- **Multi-Sheet**: Sheet Browser, Find Item in Other Sheets and Models.
- Windows dock, group, auto-hide, pin [V1 related topics].

### Shortcuts [snippet of 2022 shortcuts page]
Ctrl+F2 Clash Detective, Ctrl+F3 TimeLiner, Ctrl+F5 Animator, Ctrl+F6 Scripter, Ctrl+F8 Quantification Workbook, Ctrl+F12 Selection Tree, Shift+F2 Sets.

### Behaviour
- TimeLiner links model objects to schedule tasks (data sources: MS Project, P6 etc. [M]); Clash Detective can run time-based (soft) clashes against TimeLiner/Animator [snippet].
- Clash Detective can ignore same-selection-set clashes [snippet].
- Ribbon tabs [M]: Home, Viewpoint, Review, Animation, View, Output, plus contextual Item Tools, Render. Home panels: Project, Select & Search, Visibility, Display, Tools. Our tab structure already mirrors this.
- File formats [M]: **NWD** (all-in-one published snapshot, includes markups/viewpoints/clash results), **NWF** (federated links to source files + review data), **NWC** (cache created from CAD/BIM exporters, read-only link). Freedom/viewer reads NWD. Native readers for DWG, RVT, IFC, DGN, SKP, etc.

### Details by tool [M unless noted]
- **Selection Tree** [V1 window exists]: views Standard / Compact / Properties / Sets; right-click hide, require, set appearance, scene stats.
- **Sets**: selection sets (static) vs search sets (live rule); folders; export/import XML.
- **Find Items**: conditions on category/property/value with operators; combine with AND/OR; save as search set.
- **Clash Detective**: Tests (Rules / Select / Results / Report tabs). Types: hard, hard (conservative), clearance, duplicates. Tolerance, link to TimeLiner. Result statuses New/Active/Reviewed/Approved/Resolved, grouping, assign, auto-viewpoint, reports.
- **TimeLiner**: Tasks / Data Sources / Configure / Simulate tabs; task types (construct, demolish, temporary); planned vs actual; attach by sets; Gantt; cost columns.
- **Quantification**: takeoff via model/virtual/ 2D; catalogs; export workbook.
- **Animator**: scenes, cameras, animation sets with keyframes (transform, color, transparency); timeline playback.
- **Scripter**: events (start, timer, key, hotspot, variable) + actions (play animation, show viewpoint, set variable, pause, send message).
- **Viewpoints**: camera + hide/required + appearance + markups + section state; animations and cuts; folders.
- **Sectioning**: up to 6 planes, linked, box mode.
- **Measure**: point to point, point to multiple points, accumulate, angle, area, shortest distance; lock axis; convert to redline.
- **Redline/Tags**: ellipse, cloud, line, freehand, text; tags with IDs, comments with status.

## 2. Our `coord` tab (110 rows)
Built*: Append, Reset All, File Options, Selection Tree, Find Items, Hide overlays, Properties, Clash Detective, Coordination, TimeLiner, Quantification, Autodesk Rendering, Animator, Compare, Safety, Save Viewpoint, Views, Record, Play, Perspective, Orthographic, Top, Iso, Walk, Orbit, Pan, Zoom all, Shaded, Wireframe, X-ray, Lighting, Enable Sectioning, Plan cut, Section Z, Clear cuts, all Measure tools, Text, Erase, Add Tag, Comments, Reviews (4), Animation items, Labels, Levels, Show Grid, Split View, Full Screen, Background, Windows, Load Workspace, Site plan, Publish (ZIP/Share), Export IFC/OBJ/DXF/…, Image/Rendered/Animation, reports.
Not built: Refresh, Select/Select All/Select Same, **Sets**, Hide/Require/Hide Unselected/Unhide All, Links, Quick Properties, **Scripter**, Batch Utility, DataTools, Field of View, Align Camera, Look Around, Fly, Realism, Draw, Tag ID, Scripts, Navigation Bar, ViewCube, HUD, FBX, KML, NWD, Viewpoints report.

## 3. Gaps, prioritised

| Pri | Gap | Build in browser |
|---|---|---|
| P0 | **Sets** (selection + search sets, folders) | Store ids or rule objects; used by Clash/TimeLiner/Quantification |
| P0 | **Select / Select Same / Hide / Require / Hide Unselected / Unhide All** | Selection state + visibility overrides on the scene graph |
| P0 | **Selection Tree views** (Standard/Compact/Properties/Sets) + right-click menu | Tree from file→layer→element; alternate grouping by property |
| P0 | **Clash Detective full workflow**: tests, rules, types (hard/clearance/duplicate), tolerance, statuses, grouping, assign, viewpoints, report | AABB broad phase + triangle/segment narrow phase in worker; results table |
| P0 | **TimeLiner**: Tasks/Data Sources/Configure/Simulate, task types, planned vs actual, attach by set, playback with date overlay | Reuse `sched` data; colour by task type; timeline slider |
| P1 | **Quantification workbook** with Item/Resource catalogs, model takeoff by set | Table + catalog tree; export XLSX |
| P1 | **Animator + Scripter** (keyframes, events/actions, enable scripts) | Keyframe timeline for camera/transform/colour; event→action list |
| P1 | Viewpoint fidelity: folders, hide/required & appearance stored, section state, edit/update, animation clips | Serialise scene overrides per viewpoint |
| P1 | Sectioning: multiple planes, box mode, link planes | Clip planes (up to 6) in renderer |
| P1 | Measure: multiple points, accumulate, shortest distance, lock axis, convert to redline | Extend measure tool |
| P1 | Navigation: Look Around, Fly, Realism (collision/gravity), ViewCube, Navigation Bar, HUD, FOV, Align Camera | Camera controllers; simple capsule collision |
| P2 | Redline Draw (ellipse/cloud/line/freehand), Tag ID, comment statuses, Find Comments | Overlay canvas + comment store |
| P2 | Properties/Quick Properties, Links, DataTools (external table join) | Property panel, CSV join |
| P2 | **Formats**: NWD/NWF/NWC naming — we cannot write real binary NWD; offer our own `.tox` package and label honestly. FBX, KML exports | JSON/ZIP package; glTF/OBJ/IFC readers where possible |
| P3 | Appearance Profiler, Batch Utility, Compare detail, Multi-Sheet windows, Autodesk Rendering settings | Later |

## 4. Honesty notes
- Real NWD/NWC are proprietary; do not claim compatibility. Say "TOX package" or "IFC/OBJ import".
- Items in our tab with no verified Navisworks equivalent: Coordination (specs vs codes), Safety, Reviews (Structural/MEP/Quality/Handover), Hide overlays, Plan cut, Site plan, Disassembly/Assembly video, Project package ZIP, Share. Label as "T.O X extra".

## 5. Not verified
Exact ribbon panel contents per release, clash type names/status wording, NWF/NWC description details, Scripter action list, shortcut list beyond the snippet, Navisworks Manage vs Simulate feature split beyond Clash Detective (Manage only [V1]).
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### user · 2026-11-20T06:45:22.180Z

<details><summary>نتيجة أداة (16843 حرف)</summary>

```
# Research folder (written by background sessions)
- our_commands.json : every command currently listed in the app ribbons (program, tab, panel, command, whether built, what it runs).
- Each session writes only its own files here. Never edit the app source (c_*.js, patch_v3.py, build.py, index.html).
- Mark every claim: VERIFIED (source URL read) or FROM MEMORY. No invented values. No copying of vendor code or artwork.
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
| ACC Issues / RFIs / Submittals | Project-management data | 3LO (write depends on user permissions, VERIFIED for Submittals) | Submittals: 600 req/min per key and per user (VERIFIED: https://aps.autodesk.com/en/docs/acc/v1/overview/rate-limits/submittals-rate-limits). RFI v3 released July 2025, base path /construction/rfis/v3/projects/:projectId (VERIFIED: https://aps.autodesk.com/node/3723). Submittals write endpoints added in phases through March 2025 (VERIFIED: https://aps.autodesk.com/node/3607). | Calls yes with 3LO, subject to CORS test. |

Cost model (VERIFIED, mixed): chargeable APIs used Cloud Credits, moved to Flex tokens (Nov 2022, https://aps.autodesk.com/node/2386; end of 2025 notice https://aps.autodesk.com/node/3776); one APS page dated 27 Oct 2026 mentions an upcoming pricing change (https://aps.autodesk.com/node/3881). NOT VERIFIED: current per-unit prices. Get them in the APS console.

Account prerequisites (MEMORY): free APS developer account, an app with client ID; ACC data access also needs the project admin to add the app (custom integration) to the account. ACC itself is a paid product, not free.

**Can a pure browser app call it?** Auth: yes (PKCE). Data calls: likely, per-endpoint CORS not tested. Not possible: webhooks (need a server), Design Automation plugin build, 2LO (secret). All of it requires the user's own Autodesk login and (for paid parts) their billing. T.O X should treat APS as an optional connector, never as a dependency.

---

## B. Open source and open BIM

| Item | Licence | Language | Reusable by a browser app | Maturity / notes |
|---|---|---|---|---|
| IFC 2x3, 4, 4.3 (schema) | ISO 16739-1:2024 = IFC 4.3, adds roads, rail, bridges, waterways, ports (VERIFIED: https://www.iso.org/standard/84123.html, https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/content/scope.htm). IFC4X3_ADD2 docs = same schema + clarifications, page still marked "under development" (VERIFIED, same site). IFC2x3 and IFC4 are older ISO 16739 editions (MEMORY). | EXPRESS / STEP text, also ifcXML, ifcJSON (MEMORY) | Yes: the data model for T.O X export. Write STEP text from JS, simple subset first. | Stable standard. Real-world exporters mostly IFC2x3/IFC4 (MEMORY). |
| web-ifc (That Open Engine) | MPL-2.0 (VERIFIED by several results, one outlier says MIT; check LICENSE in repo: https://github.com/ThatOpen/engine_web-ifc) | C++ compiled to WebAssembly, JS API | YES, runs fully in browser, no server. Reads/writes IFC; IFC4X3 schema option exists (VERIFIED: https://skills.sh/openaec-foundation/thatopen-claude-skill-package/thatopen-core-web-ifc, secondary). | Active, widely used. MPL-2.0 is file-level copyleft: fine to load as a separate file, edits to its files must be shared. |
| That Open Components | licence of @thatopen/components NOT verified | TypeScript on three.js | Yes (viewer, fragments, BCF, IDS-related components per project docs, MEMORY) | Active; web-ifc-three is deprecated (VERIFIED, secondary: skills.sh page above). |
| IfcOpenShell | LGPL (VERIFIED: https://wiki.osarch.org/index.php/Free_software_libraries_for_AEC_software_development, and search results on github.com/IfcOpenShell) | C++ with Python bindings; also a WASM/JS build exists (MEMORY) | Desktop/server side: validation, IfcPatch, IDS check (ifctester), clash. A Pyodide-in-browser route exists in community (MEMORY, not tested). | Mature, the reference open toolkit. |
| Bonsai (ex BlenderBIM) | GPL-3.0-or-later (VERIFIED: search result tool table, github.com/IfcOpenShell family) | Python, Blender add-on | No (needs Blender). Useful as the "desktop model editor" a Blender MCP could drive. | Mature, active. |
| xBIM | CDDL per one source only (VERIFIED weakly: https://wiki.osarch.org/index.php/Free_software_libraries_for_AEC_software_development) | C# / .NET | No (server/desktop). | Mature. Re-check licence before use. |
| FreeCAD BIM workbench | LGPL (MEMORY; not verified this session) | Python/C++ | No. Desktop; scriptable headless, so a server-side agent target. | Mature but UI-heavy. |
| Speckle | Server code Apache-2.0 except enterprise modules (workspaces, gatekeeper) under a separate licence (VERIFIED: https://github.com/specklesystems/speckle-server and review page via search). Hosted platform is commercial. | TypeScript server, viewer, connectors in C#/Python | Speckle viewer and object model are JS; a free hosted account + token could work from a browser (CORS NOT tested). | Active. Connectors for Revit/AutoCAD exist (MEMORY). |
| BIMserver | Mostly AGPLv3 per project; IFCEngine part is NOT open source (VERIFIED: https://github.com/opensourceBIM/BIMserver/wiki/License) | Java | No: server. | Older, less active than Speckle (MEMORY). Avoid as default. |
| buildingSMART bSDD | Free service by buildingSMART (VERIFIED: https://www.buildingsmart.org/?p=29545) | REST/GraphQL API (MEMORY) | Yes: simple HTTPS lookups of class names and properties from the page (CORS not tested). | Production service. |
| BCF (issues) | Open standard; XML file (.bcfzip) and REST BCF-API (VERIFIED: https://github.com/buildingSMART/BCF-API, https://github.com/buildingsmart/bcf) | XML / JSON | Yes: T.O X can read/write .bcfzip with JSZip, no server. | Mature file format, v2.1 / v3.0 (MEMORY). |
| IDS (Information Delivery Specification) | buildingSMART open standard, machine-readable information requirements (VERIFIED, description only: https://catenda.com/glossary/buildingsmart-standards) | XML (XSD) | Yes: write IDS XML from the EIR step, check IFC with web-ifc in JS (own checker) or ifctester on desktop. | IDS 1.0 released 2024 (MEMORY). |
| openCDE APIs | Foundation API + Documents API 1.0 + BCF API (VERIFIED: https://github.com/buildingSMART/technical.buildingsmart.org/blob/main/openCDE-API.md, https://github.com/buildingSMART/documents-API). Described as still maturing (VERIFIED, secondary). | REST + OAuth2 | Possible client side, needs a CDE that implements it. | Early. Do not depend on it. |

Browser reuse summary: web-ifc (read/write IFC), BCF zip, IDS XML, bSDD lookups, optionally Speckle viewer. Everything else (IfcOpenShell, Bonsai, FreeCAD, xBIM, BIMserver) is desktop/server: reach it through the agent bridge (see AGENT_CONTROL.md), not inside the page.

---

## C. Standards for the project lifecycle

**ISO 19650-2 delivery phase, 8 stages** (VERIFIED list: ANSI preview https://webstore.ansi.org/preview-pages/ISO/preview_ISO+19650-2-2018.pdf and DIN TOC via search; clause detail for stages 6-8 NOT read):
1. Assessment and need (reference info, CDE, information protocol)
2. Invitation to tender (tender requirements, evaluation criteria)
3. Tender response (pre-appointment BEP, capability and capacity, mobilization plan, risk register)
4. Appointment (confirm BEP, responsibility matrix, MIDP)
5. Mobilization (resources, IT, test production methods)
6. Collaborative production of information
7. Information model delivery
8. Project close-out

**Document set** (VERIFIED, secondary: https://www.cdbb.cam.ac.uk/files/bep_guidance.pdf and designingbuildings wiki):
- EIR: Exchange Information Requirements, from the appointing party: what information, format, milestones.
- BEP: lead appointed party's plan to meet EIR; pre-appointment then confirmed post-appointment.
- MIDP: project-wide schedule of deliverables; living document.
- TIDP: each task team's part of the MIDP.
- A 2026 draft revision reportedly renames BEP to "Information Production Plan", final expected 2027: single secondary source, NOT verified.

**LOIN / LOD:** ISO 7817-1:2024 "Level of information need" is current (VERIFIED: https://www.iso.org/standard/82914.html; adopted from EN 17412-1, which is withdrawn). It moves away from LOD/LOG/LOI labels towards specifying need per purpose, per object (VERIFIED, secondary: https://constructionmanagement.co.uk/new-level-of-information-need-standard-published/). LOD 100-500 labels (AIA/BIMForum) are still widely used by contracts (MEMORY). Whether LOD is formally superseded: not stated by sources.

**COBie:** spreadsheet/IFC subset for handover asset data (MEMORY, no URL read; I did not verify details). Treat as a Phase-8 export from the model; the IFC Facility Management Handover MVD is the formal route (MEMORY).

**7D (asset/facility management data):** the usual convention is 3D model, 4D schedule, 5D cost, 6D sustainability, 7D facility management (MEMORY; conventions vary by author, no authoritative standard found). For T.O X: 7D = asset register (type, serial, warranty, maintenance interval) exported at handover.

---

## D. Recommended lifecycle for T.O X

Principle: map ISO 19650 stage names, but keep it light for a browser tool. Agents propose, humans approve at gates. Every output is stored with source and "verified / assumed" flag. No invented values: missing input becomes a question to the client.

| # | T.O X stage (ISO 19650-2 stage) | Agent role does | Automatic checks | Human gate | Open tool / format |
|---|---|---|---|---|---|
| 0 | Brief intake (1 Assessment and need) | **Client-liaison agent** turns text brief into structured requirements, asks missing questions (site, area, budget, code, climate) | Completeness list; unit sanity | G1: client confirms brief summary | Plain JSON; bSDD for class names |
| 1 | Information requirements (1-2) | **Information manager agent** drafts EIR and IDS | IDS XML schema-valid | G2: client approves EIR | IDS XML, BCF for questions |
| 2 | Plan (3-4) | **Project-manager agent** drafts BEP, MIDP, TIDP, responsibility matrix, programme (P6 tab) | Each deliverable has owner, due, LOIN | G3: lead approves BEP/MIDP | Own register in T.O X; export CSV/XER later |
| 3 | Setup (5 Mobilization) | **Information manager agent** creates folder/CDE structure and naming, tests the exchange formats | Naming rule check; round-trip test IFC | none (auto) | Folder tree, web-ifc test |
| 4 | Concept and analysis (6) | **Architect, civil, structural agents** produce massing, site grading, preliminary sizing | Own calc modules; units; code-clause list shown | G4: designer signs concept | T.O X tabs; calculations flagged "preliminary, not stamped" |
| 5 | Detailed design (6) | **Architect, structural, MEP, electrical agents** model in the tabs | Rule checks per discipline; schedule from model | G5: licensed engineer review per discipline | IFC export via web-ifc |
| 6 | Coordination and review (6) | **Coordination agent** runs clash, IDS check, compares LOIN, writes issues | Clash list; IDS pass/fail; missing-property list | G6: coordination meeting decision per issue | BCF issues; optional IfcOpenShell on desktop for clash/IDS |
| 7 | Delivery and approval (7) | **Reviewer agent** assembles package, checks MIDP vs delivered | Every MIDP item delivered or waived | G7: client/authority acceptance | IFC + BCF + PDF drawings |
| 8 | Handover and close-out (8) | **Asset agent** builds COBie/asset register, archive, lessons learned | Mandatory COBie fields filled | G8: client signs handover | COBie sheet, IFC |

Gate rules: a gate cannot be passed by an agent. The page shows a stage banner, an indicator of open questions, open issues, and unapproved outputs. Stage cannot advance with blocking issues. Everything an agent produced is tagged "AI draft" until a person approves.

Boundary statement for the UI: outputs are drafts for qualified engineers; T.O X does not replace stamped design (professional responsibility rests with licensed engineers).

---

## What was NOT verified
- Current APS per-unit prices and whether Cloud Credits are fully retired (conflicting pages).
- CORS behaviour of each APS endpoint from a browser origin (no live test).
- Licences of xBIM (one source), FreeCAD BIM, @thatopen/components; speckle-sharp licence.
- ISO 19650-2 clause content of stages 6-8; COBie details; 7D definition (convention only).
- Full text of any ISO standard (paywalled); only titles, abstracts and tables of contents.
- Most search results were excerpts, not full pages.
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T06:45:26.109Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research && cat gap_autocad.md gap_civil3d.md gap_plant3d.md | cut -c1-600; echo ======; head -c 9000 AGENT_CONTROL.md"
}
```

### assistant · 2026-11-20T06:45:27.149Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs && cut -c1-400 MEETING_ROOM.md | head -250"
}
```

### user · 2026-11-20T06:45:28.276Z

<details><summary>نتيجة أداة (10039 حرف)</summary>

```
Exit code 1
# AutoCAD ribbon vs our "draft" program: gap list

Provenance: **VERIFIED** = Autodesk help page opened. Everything else is **FROM MEMORY** (AutoCAD 2025/2026 ribbon as I remember it; not re-checked panel by panel).
Verified pages (help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-Core/files/):
- GUID-57CDDB6C-B12B-46CE-B9C5-22EFC17258FF.htm : "To Draw Lines" says Home tab > Draw panel > Line (confirms the Home/Draw path).
- GUID-E8C1190C-A26C-484C-ADDD-DDF81666F69F.htm (LINE), GUID-B1A185EF-07C6-4C53-A76F-05ADE11F5C32.htm (TRIM), GUID-E908848F-4621-43D2-B377-FD3FBC2B8848.htm (DIMLINEAR), GUID-ACC319C8-34EA-4D9D-981E-B69B7B187400.htm (polylines).
- Could NOT open: a single Autodesk page listing every 2026 ribbon tab/panel (autodesk.com support pages return Access Denied; help search gave no full list). The tab list below is therefore FROM MEMORY.

## Real tabs (from memory)
Home, Insert, Annotate, Parametric, View, Manage, Output, Add-ins, Collaborate, Express Tools, (Featured Apps). Ours has the first 7 plus nothing for the last four.

## Our extras / questionable
- `Note in 3D`, `Export SVG`, `Share`, `Measure` palette: not recognised as AutoCAD ribbon commands (see cmd_autocad.json).
- Our Home/Draw puts `Wipeout`, `Revision Cloud` (real: Draw dropdown / Annotate>Markup, OK). Our Home/Modify `Align` real, OK.

## Priority 1: core drafting / design (missing in ours)
| Real tab/panel | Missing | Browser build note |
|---|---|---|
| Home/Draw | Arc and Circle sub-methods (3-point, centre, tangent), Donut | Add submenu per command; each is a different input sequence on the same canvas tool |
| Home/Draw | Rectangle chamfer/fillet options, Polygon inscribed/circumscribed | Option keys in the tool's command-line prompt |
| Home/Modify | Scale reference option, Stretch, Array path/polar variants (we have Array only as one), Overkill, Pedit multiple, Break at point, Fillet polyline | Mostly geometry ops; reuse polyline library |
| Home/Modify | Move/Copy with base point + "Displacement", Copy multiple mode | Command-line option state machine |
| Home/Annotation | Dimension types shown in dropdown (we expose in Annotate only), Multileader | Already in Annotate; add shortcut dropdown |
| Home/Layers | Layer states, Layer Walk, Off, Uniso/Merge/Delete, Match to object | Layer panel state list in memory; trivial |
| Home/Block | Block editor (BEDIT) with parameters/actions, Create Block/Write Block (WBLOCK) | Block definition JSON; editor as sub-canvas |
| Home/Properties | ByLayer/ByBlock drop-downs, Quick Properties | Property bar bound to selection |
| Home/Utilities | Quick Select, Select Similar | Filter selection by property/type |
| Home/View | Viewport/named view shortcuts (covered in View) | n/a |

## Priority 2: documentation and drawing production
| Real | Missing | Browser note |
|---|---|---|
| Insert/Block Definition | Define Attributes, Manage Attributes (ATTMAN), Block Editor, Create Block | Attributes as key/value on block refs |
| Insert/Reference | Xref manager (XREF), Image, Underlay Layers, Point Cloud (RCS) | Xref = load second DWG JSON; point cloud via Potree-like viewer |
| Insert/Import | Import (many formats), PDF Import, Markup Import | Only DXF/PDF.js realistic |
| Insert/Data + Linking & Extraction | Data link manager, field insertion (FIELD), Extract data | Field = text with a formula that re-evaluates |
| Annotate/Text | Text Style, Annotative scaling, Align text, Text Editor tab | Style dialog sets font/height/width |
| Annotate/Dimensions | Dim Break, Space, Jogged/ Ordinate/ Center Mark, Dim Edit, Quick Dimension (QDIM), Inspect, Tolerance | Each dimension kind = a renderer + measuring rule |
| Annotate/Leaders, Tables | Table Style, Data link table (we have link), Insert field | Table object as rows/cols grid |
| Annotate/Markup | Revision Cloud shape options, Markup Set Manager | Cloud already; markup set is a list |
| Annotate/Annotation Scaling | Add/Delete Current Scale, Annotative object toggle | Scale list per object; render by viewport scale |
| Output/Plot | Plot style table (CTB/STB), Plot stamp, Publish dialog, Plot to PDF with layouts | We have Plot/Batch; add layout tabs (paper space) |
| Manage/CAD Standards | Standards checking is there; add Layer Translator maps editor | JSON maps |

## Priority 3: advanced and 3D
| Real | Missing | Browser note |
|---|---|---|
| Home/Modify (3D) | 3D Move/Rotate/Mirror/Array, Align 3D, Fillet Edge, Extrude/Presspull | Needs Three.js; large job |
| Home/Draw (3D) | Box, Cylinder, Sweep, Loft, Revolve, Mesh primitives | Three.js geometries |
| Visualize tab (some versions) / View | Render, Materials Browser, Lights, Camera, Section Plane | Three.js + PBR |
| View/Coordinates & UCS | UCS icon, World UCS, Face UCS, Origin | Transform matrix per viewport |
| View/Viewport Tools | Viewcube, Navigation bar, SteeringWheels | Canvas controls |
| View/Interface | Layout tabs, File tabs, Layout viewports (MVIEW/MVSETUP) | Paper-space vi

... [6556 characters truncated] ...

 Help > What's New in Civil 3D 2026.
# Gap: AutoCAD Plant 3D vs T.O X `plant`

Legend: **[V]** = read on Autodesk help. **[M]** = memory, not verified. Own wording.
Data in `cmd_plant3d.json` (83 keys; 5 verified, 47 memory, 31 app-specific).

## Verified sources (read)
- About the Ribbon (all tabs/panels below): https://help.autodesk.com/cloudhelp/2024/ENU/Plant3D-UserGuide/files/GUID-D792AEF2-E0E9-450A-9C5D-970F156E4AE4.htm
- Project Manager (Home > Project panel, command `projectmanager`, project name list, Publish, Reports, Data Manager, Export/Import data): https://help.autodesk.com/cloudhelp/2018/ENU/Plant3D-UserGuide/files/GUID-B05A7C7B-A0CD-4484-813D-84C5B212C8C8.htm
- Visibility of Plant 3D objects (separate from AutoCAD layers): https://help.autodesk.com/cloudhelp/2021/ENU/Plant3D-UserGuide/files/GUID-118AAFEF-9E27-48A3-86FD-DE1E67F3089B.htm
- Ortho insulation tool (Home > Ortho Views panel; Ortho View tab): https://help.autodesk.com/cloudhelp/2021/ENU/Plant3D-UserGuide/files/GUID-01868409-F942-4F00-9DAF-FCAC69D7C4B9.htm
- Not read: individual pages for Equipment, Pipe Supports, Spec Editor, Iso annotation commands (only panel names confirmed via search results).

## Real ribbon [V]
- **3D Piping > Home**: Project, Part Insertion, Ortho Views, Compass, Elevation & Routing, Slope, Pipe Supports, Equipment, Visibility, View, Layers, Plugin.
- **Isos**: Iso Creation, Iso Annotation, Export.
- **Structure**: Parts, Modify, Cutting, Visibility, Export, Views, Layers.
- **Ortho Editor** (contextual): OrthoCube, Select Library, Output Appearance, Output Size, Location Offset, Create.
- **Ortho View** (contextual, green): Ortho Views, Plant Object Tools, Single Line Piping, Table Placement & Setup, Annotation, Dimensions, Model Viewports, Layers.
- **P&ID Home** (other workspaces): Project, P&ID Schematic, Line, Line Group, Validate, Layers, Block, Annotation, Properties, View, Utilities.
- Not verified: Project Browser-like Project Manager tabs (Plant 3D DWG, P&ID DWG, Orthographic DWG, Isometric DWG) [M for exact tab names; Ortho and Iso tab mention seen in search snippets]. Spec Editor, Catalog Editor, Properties palette, Tool Palette, Data Manager details [M].

## Missing in ours, by priority
| Pri | Real feature | Gap | Browser idea | IFC / data |
|---|---|---|---|---|
| P1 modelling | Spec-driven piping: Spec Editor / Catalog, pipe route with auto fittings, slope, elevation & routing panel [M; panels V] | most Home items unbuilt | spec JSON (size, class, parts) + route tool that picks fittings | IfcPipeSegment, IfcPipeFitting, IfcValve; Pset_PipeSegmentTypeCommon |
| P1 | Equipment: Create from templates (tank, vessel, pump), nozzles [M] | Create/Attach/Nozzle unbuilt | parametric templates + nozzle connector points | IfcTank, IfcPump, IfcFlowTerminal; IfcDistributionPort for nozzles |
| P1 | Valves, custom parts / placeholders [M] | unbuilt | catalog of valve shapes; placeholder box | IfcValve, IfcBuildingElementProxy |
| P1 | Pipe supports [M] | unbuilt | support symbol snapped to pipe | IfcDiscreteAccessory / IfcPipeSupport? (verify class) |
| P1 | Structure tab: members, railing, stairs, ladders, plates, footings; cutting [V panels, M tools] | unbuilt | profile library + member generator | IfcBeam/IfcColumn/IfcMember, IfcRailing, IfcStair, IfcFooting |
| P2 documentation | Isos: production/quick iso, annotation, PCF [V panels, M tools] | partial | isometric projection of pipe graph on SVG, with BOM table; PCF text writer | IfcPipeSegment graph; PCF text |
| P2 | Ortho views (create/edit, insulation symbol, dimensions, single-line) [V] | partial | 2D projection with hidden-line, annotation layer | none (derived) |
| P2 | Compass, Layers, View panels [V] | missing | north arrow + layer table | none |
| P3 quantities | Project Manager / Data Manager reports, line list [V PM] | BOQ only | JSON report engine over components; CSV export | IfcElementQuantity, IfcPropertySet |
| P3 | P&ID side: lines, valves, instruments, validate, line list [V panels] | none | SVG P&ID editor with tags linked to 3D lines | IfcDistributionSystem / link by tag |
| P4 systems | Line groups, validation, publish to DWF, import/export data [V PM menu] | missing | line group table, consistency checks | IfcSystem |
| P5 | Plugin panel, Navisworks export (NWC) [M] | NWC unbuilt | export IFC instead; NWC needs vendor tool | IFC |

## Ours but not in Plant 3D (31 tagged app-specific)
Compare panel (Colour by system, X-ray, Ghost concrete, Hide overlays), Parts list, Families, Section/Side/Adjacent View, Iso view, Analysis tab (Clashes, Coordination, MEP review, Safety, Pump and pipe calcs, Engineering analysis, HVAC), Output (Iso sheet A1, Drawing sheet, Render, Screenshot, OBJ, BOQ XLSX, Share, ZIP). Keep but label "T.O X extra".

## Notes
- Key `plant|X-ray` is the same app toggle in two panels.
- Several Iso annotation and Structure tool names are our guesses of real names; marked unverified in `src`.
(eval):1: ===== not found
```

</details>

### user · 2026-11-20T06:45:28.694Z

<details><summary>نتيجة أداة (2249 حرف)</summary>

```
<persisted-output>
Output too large (36.8KB). Full output saved to: /Users/M7/.claude/projects/-Users-M7-Documents-ai-trading-dashboard/38f040aa-93ba-4b4f-aa1d-5553cdcf4ae7/tool-results/bwk6953q5.txt

Preview (first 2KB):
# MEETING ROOM: agreements, decisions and status

Template used: **BVT-1 (BIM Viewer Template)**. See `template/BVT-1/README.md`. Any new project reuses the same idea: copy the source, edit only the PROJECT blocks.

Project: Sewage Lift Station (sheets BIS-ME-LST-01 plan, 02 roof plan, 03 section A; scale 1:25).
Live page: `index.html` (GitHub Pages). Source: `src/lift_station_3d.html`.

## Decisions agreed with the owner

- Concrete thickness: 430 mm for every wall and slab (measured on sheets; the owner asked to treat all concrete the same). The remark "2 x 2" is ignored.
- Wet well: round, internal Ø3000; depth 5.25 m (B.L +1159.76 to top +1165.01). Outlet chamber: internal 2000 x 3200, floor +1162.91.
- Openings (sheet 02): 3000 x 800 along the pump row; 800 x 800 on the well, inlet side next to the crane; 800 x 800 on the outlet chamber roof. Two Ø100 GRP vents on the well top.
- The only crane of the station is the 1 t, 360 degree electric jib crane. "Crane 2000 Kg" printed on the sheets belongs to the building plan in the background.
- Pump capacity conflict on the sheets: 8 L/S on sheet 01 and 7 L/S in the table. Open: confirm before ordering.
- The page must not carry a "limits / honesty" section. Honest status goes in the chat replies and in this file.
- Drawings follow ISO 128 conventions: wide cut outlines, narrow hatch for cut reinforced concrete, chain dimensions, level symbols, section marks, tags with leaders, scale bar. Levels can be shown relative to G.L (+0.00).
- Egyptian Code (ECP 203): the reference is written in the sheet notes. Reinforcement, concrete cover and crack-width limits are NOT invented: they stay with the structural design. A web search did not return the exact cover values for wet wells.
- Hover on any element shows its data (code, family, type, IFC class, quantity, brand, cost, LOD). Cost and brand can be typed in (BIM 5D style). Families can be edited like Revit types.
...
</persisted-output>
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T06:45:32.110Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs && sed -n 1,400p MEETING_ROOM.md | cut -c1-330 | sed -n 14,140p; echo; grep -n \"^#\" MEETING_ROOM.md | head -60"
}
```

### assistant · 2026-11-20T06:45:33.423Z

**أداة:** `Bash`

```json
{
 "command": "cd /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research && head -c 6000 AGENT_CONTROL.md; echo ====; head -c 2500 gap_civil3d.md; echo ===; head -c 1500 coohom_tab_spec.md; head -c 1200 sketchup_tab_spec.md"
}
```

### user · 2026-11-20T06:45:34.124Z

<details><summary>نتيجة أداة (5530 حرف)</summary>

```
Exit code 1
# Agent control research for T.O X (2026-11-20)

## ملخص بالعربي (5 سطور)
1. الصفحة عندها فعلاً `window.TOX` و جسر WebSocket (c_hub.js): أوامر تتعرض وتتشغل بـ id، وحالة، وتنبيهات، ومستندات. ناقصها: وسايط للأوامر، نتيجة للأمر، صلاحيات لكل أمر، وسجل تدقيق دائم.
2. أحسن طريق لوكيل خارجي (Claude Code / Gemini CLI / ChatGPT): سيرفر MCP محلي صغير بيتكلم WebSocket مع الصفحة؛ والصفحة ممكن كمان تسجل أدواتها في المتصفح عبر WebMCP لو المتصفح بيدعمه (لسه تجريبي).
3. للأدوات المكتبية: سيرفرات MCP جاهزة لـ Revit (رسمي من Autodesk، Apache 2.0، Revit 2027) و AutoCAD و Blender (مجتمع)؛ كلها بتشغّل كود على جهازك فمحتاجة موافقة بشرية.
4. المخاطر الأساسية: حقن أوامر من محتوى (prompt injection)، سر الجسر المخزّن في localStorage، منفذ CDP مفتوح؛ الحل: صلاحيات لكل أمر + موافقة المستخدم + سجل + حدود.
5. غير متأكد منه: تفاصيل WebMCP الحالية، دعم CORS لكل مزوّد نموذج، ترخيص سيرفرات المجتمع، وإمكانية تشغيل n8n MCP على نسختك.

## Evidence labels
- **VERIFIED** = seen in a search result text from the cited URL on 2026-11-20 (excerpt, not always the whole page).
- **READ** = read directly in the T.O X source (read-only, `c_hub.js`).
- **MEMORY** = my own knowledge, no URL read.
- No vendor code or artwork copied.

---

## 1. What T.O X already has (READ: `scratchpad/c_hub.js`, 6986 bytes)

- `window.TOX` = frozen object, `version:'1'`, methods from `TOXAPI`:
  - `commands()` -> list of `{id,en,ar,help}` from `XC` (every command with a title)
  - `run(id)` -> runs `XC[id].run()`, returns `true` or throws `unknown command`. **No arguments, no result data.**
  - `state()` -> project name, current tab, tab types, history position, docs count, summary
  - `pulse()` -> alert items `{severity,text}`
  - `docs()`, `addDoc(o)` (fields truncated: subject 200, body 8000), `setStatus(ref,st)` (validates ref and status), `search(q)`, `summary()`
- WebSocket bridge (`hubConnect`, `hubHandle`): off by default; JSON `{id, token, method, params}` -> `{id, result|error}`; requires shared secret of 8+ chars; warns with confirm() if the URL is not loopback (`127.0.0.1`, `localhost`, `[::1]`); keeps last 60 log lines in memory; panel `p_hub` under ribbon "Agents".
- The Agent panel (`p_agent`) already calls model APIs from the page (per the hub text: Claude, Gemini, OpenRouter, Mistral, OpenAI-compatible local servers). Keys stay in the browser.
- The hub text mentions `docs/AGENT_BRIDGE.md`. I did not check that it exists.

Gaps against what the owner wants (agents that control tools, ask questions, show indicators, open/close tabs):
1. `run(id)` cannot pass arguments (no "draw wall from A to B", no "open tab X").
2. No structured result or error codes; no way to read back the effect of a command.
3. No per-command permission class: an agent that can `run` can run anything in `XC`, including destructive commands.
4. No human-approval prompt for risky commands.
5. Audit log is 60 lines in memory only.
6. Secret stored in plain `localStorage` (`xto-hub`): readable by any script in the same origin and by browser extensions.
7. No "ask the user" channel and no "indicator" API for agents.
8. The WebSocket token is sent in each message (fine on loopback, bad on a remote `ws://`; use `wss://` only).
9. `hubHandle` has no rate limit and no origin/session binding.

---

## 2. Options compared

### 2.1 MCP (Model Context Protocol)
- Spec: servers expose tools; HTTP transports can use OAuth 2.1 (server = resource server; PKCE required for clients in the 2025-03-26 revision; tokens never in URL; 401 / 403 semantics). Authorization is optional; STDIO servers should take credentials from the environment instead. VERIFIED: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization and https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization. Newer revision 2026-07-28 prefers Client ID Metadata Documents and treats Dynamic Client Registration as deprecated fallback (VERIFIED: https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization).
- **Browser MCP**: an MCP server that controls a browser (see 2.4).
- **Filesystem MCP**: reads/writes local files. Risk: exposes the disk; restrict to one project folder (MEMORY).
- **Custom MCP server for T.O X**: a small local process (Node or Python) that (a) speaks MCP over STDIO to Claude Code/Desktop, Gemini CLI, etc., and (b) holds a loopback WebSocket the page connects to (the existing hub). Each MCP tool maps 1:1 to a TOX method. This reuses `c_hub.js` unchanged on the page side. (Design, MEMORY on client support: Claude Code and Claude Desktop support MCP STDIO; other vendors' support changes often, check each.)
- Needs from the user: Node/Python on the machine, one config line in the agent client, a shared secret. No cloud key for the bridge itself.
- Risks: tool-result text from documents/web is untrusted data and can carry prompt injection; a local MCP server runs with your user rights (MEMORY, general MCP practice).

### 2.2 Function calling (no MCP)
- Every major API (Claude, OpenAI, Gemini, Grok, OpenAI-compatible local servers like Ollama/LM Studio) accepts a list of tool definitions with JSON-schema parameters and returns a tool call that your code executes. Behaviour and schema dialect differ slightly per vendor (MEMORY: I did not read each vendor's docs in this session; the search for Gemini/OpenAI docs returned nothing usable).
- Fit for T.O X: the in-page Agent panel can run the loop itself: send tools list, get a tool call, execute via `TOX`, send(eval):1: === not found
```

</details>

### user · 2026-11-20T06:45:34.779Z

<details><summary>نتيجة أداة (18062 حرف)</summary>

```
- Pump capacity conflict on the sheets: 8 L/S on sheet 01 and 7 L/S in the table. Open: confirm before ordering.
- The page must not carry a "limits / honesty" section. Honest status goes in the chat replies and in this file.
- Drawings follow ISO 128 conventions: wide cut outlines, narrow hatch for cut reinforced concrete, chain dimensions, level symbols, section marks, tags with leaders, scale bar. Levels can be shown relative to G.L (+0.00).
- Egyptian Code (ECP 203): the reference is written in the sheet notes. Reinforcement, concrete cover and crack-width limits are NOT invented: they stay with the structural design. A web search did not return the exact cover values for wet wells.
- Hover on any element shows its data (code, family, type, IFC class, quantity, brand, cost, LOD). Cost and brand can be typed in (BIM 5D style). Families can be edited like Revit types.
- Autodesk logos or product names are not placed on the sheet. The sheet has a free "format label" field.

## Features built

3D model (about 35 parts, detailed flanges, bolts, supports, crane, odor unit), views and 360 look-around points, ghost concrete, water and levels, parametric edit panel, multi-plane section cut, 2D drawings (PDF, SVG, DXF), drawing sheet (PDF, PNG, SVG, DXF) with editable title block, notes, legend and 3D callouts, disassembly/

## Validation status

- Checked with open-source readers: DXF (ezdxf, no audit errors), IFC2X3 (ifcopenshell: 57 products with geometry created, 0 failures), XLSX (openpyxl), PDF (pypdf), SVG (XML parse).
- NOT tested: opening any file in AutoCAD, Revit, Plant 3D or Navisworks. DWG and native Revit files (.rvt, .rfa) cannot be produced in a web page. DXF to DWG: Save As in AutoCAD or the ODA File Converter.
- NOT tested: the page on phones and Safari.

## Open items

- Electrical specifications (control board, cables, starters, VFD).
- Pipe lengths beyond the model, valve bodies, ladder length, slab thicknesses if different from the walls.
- Pump capacity (7 or 8 L/S) and pump model.
- Water table level (dewatering) and soil data.
- Reinforcement design and bar schedule (structural engineer).
- Whether the concrete under the outlet chamber is solid (assumed solid).

## 4D, safety, clashes, sharing, agents (added later)

Agreed with the owner:
- A 4D schedule drives the model: parts appear as activities progress. Durations, lags, supplier lead times and crews are editable assumptions.
- Site simulation: workers, vehicles, supplier deliveries, materials on site and exclusion zones move with the timeline. Everything has hover data.
- One icon hides all data overlays and tooltips; the model and its titles stay.
- Clash detection: model clashes (mesh-level bounding boxes), clearances (maintenance, ladder, crane arm, headroom) and time-based conflicts (workers near vehicles, the crane swing radius, the open excavation).
- Hazard register with ISO references (ISO 45001, ISO 12100, ISO 7010, ISO 3864-1, ISO 12480-1, ISO 9927-1, ISO 31000, local law); severity and likelihood are editable.
- Accepting an item teaches the tool to ignore it next time. Lessons are recorded and exportable.
- Notes: 3D note pins and pen/text markup on the 2D drawings (kept in exports).
- Sharing: WhatsApp, Telegram, phone share, copy link. The link carries the state in the `#s=` hash.
- Agents: `window.BVT.call(...)`, postMessage, and "Copy agent brief". See `docs/AGENTS.md`. Learning: `docs/LEARNING_LOG.md`.

Not decided yet: real schedule data, real site layout, HSE officer review.

## Project calculations received (amr.rar, 2026-11-19)

- Mechanical calc: peak flow 14.70 L/s, 3 pumps (2 duty + 1 standby), calculated 7.35 L/s each, SELECTED 8.00 L/s. This settles 7 vs 8: use 8 L/s.
- Structural calc (44 sheets, SAP plate model): ACI 318-19, ACI 350, ACI 350.3, ACI 224R, SBC 301/304, ASCE 7. Concrete C40, steel fy 420. Cover: 50 mm soil and internal water faces, 40 mm walls, 25 mm slabs. Bearing 200 kN/m2; water table not considered (base to water table: nil).
- Thickness and bars in the calc: 400 mm with T16@150, 300 mm with T14@150, 200 mm with T12@150. DECIDED 2026-11-19: the structural calculation governs. The model now uses well wall 400, base 400, well top slab 200, chamber walls 300, chamber floor 400, chamber roof 200 mm (six editable parameters). The old 430 mm rule is replac
- Earlier note about ECP 203 is replaced: the project design basis is ACI/SBC.
- ME-GLY-01.dxf (174 MB) is the site plan; not loaded yet.

Entered on the drawings (2026-11-19): water levels on the section now follow the mechanical calc (H.W.L start +1161.28, H.H.W.L +1161.38). Sheet page 2 carries three tables: mechanical design data, structural design data, site context (from ME-GLY-01.dxf, label-to-label distances). Sheet notes now state 8.00 L/S at 10.00 m head 

Site plan in 3D (2026-11-19): new tab "Site plan" shows ME-GLY-01.dxf linework (4,164 segments in 5 categories), the UG sewage storage tank 1000 m3 (2 cells) with 4 pits, the potable and firefighting tank 2500 m3, the workshop/irrigation complex, the electrical building, pipes (100 runs, buried 1.2 m assumed) and labels, aligned


---
## Session log 2026-11-19: T.O X (Technical Office X) — what is done, what is running, what is left
Read this first if you open the work from another account or machine. Full conversation text is in `docs/CONVERSATION_LOG.md` (the repo may be public; remove that file before publishing if you do not want it readable).

### How to resume
1. Sources are in `src/build/` (chunks `c_*.js`, `patch_v3.py`, `build.py`, base `v2_backup.html`, `lib/`). Run `cd src/build && python3 patch_v3.py && python3 build.py` → writes `src/lift_station_3d.html` and `index.html` (one file, about 1.8 MB).
2. Tests are Playwright scripts in `src/build/tests/` (`node t46.js <path to Chrome for Testing>`; they load `file:///tmp/ls_index.html`, so copy `index.html` there). Code is reached in tests through `__lsv.ev("...")`.
3. Conventions: command = `XCMD(id,icon,en,ar,run,on)`; ribbon = `RIB` array; dock widget = `WX.defs.<id>` set inside a `wxDefs` wrapper; panel refresh on open = `WXR.<id>`; bilingual text = `b2(en,ar)`; DOM helper `el(tag,props,...kids)`. A new chunk is added to the list in `patch_v3.py`. Top-level names must be unique across c
4. User rules: short Egyptian Arabic; never invent values (prices, soil data, win numbers); no "limits" section on the page; ask before publishing (the page holds Royal Saudi Air Force project data and coordinates; the entry gate is only visual); say what was not tested.

### Done (headless-tested with mocks; real-browser and live-internet behaviour NOT verified)
- Core (earlier): 3D/BIM model, parametric edit, sections, sheets, BOQ and cost, IFC2X3 / DXF / OBJ / XLSX, Primavera-style CPM schedule (XER, MSP XML), timeline dock with link-motion, measure, CAD editor, site plan in 3D, rebar, scenarios, Monte Carlo risk, codes library (Egypt, Saudi, USA), calculation sheets and review, coord
- Document tabs (`c_tabs.js`): Start page + tabs per discipline (model, drafting, schedule, survey, coordination, detection, take-off, levels, simulation, analysis, office); each tab keeps its own layout. Start page offers tabs, project, role, learning, web search.
- Player: Quran radio filtered to Egypt and Saudi from the mp3quran.net station list (needs internet), custom stream URL, YouTube link embed, pop-out small browser window for radio and for video, web widget.
- Technical office and document control (`c_dc.js`): register (22 document types: letters, RFI, submittal, shop drawing, MS, MIR, IR, NCR, VO, IPC, claims, MOM, transmittal, reports...), incoming / outgoing, auto reference numbers, status, due dates, history, link to a schedule activity, print / PDF, save HTML, email (mail app a
- Share and social (`c_social.js`): caption and hashtag writer (Arabic / English, tones), post-image maker for Instagram, Story / Reels / TikTok, Facebook / LinkedIn, X, YouTube, Telegram sizes, share intents for Telegram, WhatsApp, Facebook, LinkedIn, X, Reddit, email; Instagram / TikTok / Discord / YouTube / GitHub open the si
- GIS and environment (`c_env.js`): sun path and seasons (computed), day cycle on the 3D light, optional shadows; wind rose from Open-Meteo plus ASCE 7 velocity pressure; ECP-neutral ASCE 7 equivalent lateral force; USGS recent earthquakes; clear-sky solar and NASA POWER climate; USCS helper, Darcy / Sichardt dewatering, SoilGri
- Project control (`c_ctrl.js`): Pulse (rules over documents, activities, risks, data date; handover readiness with the named blockers), calendar (document due dates, milestones, critical activities, asset dates, reminders; .ics export; Google Calendar links), Telegram bot (token and chat id; /status /due /handover /rfi /ncr /no
- Teamwork (`c_team.js`): teams and members, separate 120-step history per team, named versions with roll-back, activity log (CSV), live session (BroadcastChannel in the same browser; WebRTC copy-paste link between devices), chat, camera share, search everywhere (Ctrl+Shift+F). Roles are cooperative, not security.
- Workspace comfort (`c_ui2.js`): density levels, zoom 50–140 %, collapse arrow for the top bars; autosave every 5 s; 120 steps kept in IndexedDB and restored after a restart (tested with a page reload); hover cards with a moving picture for every ribbon button, tab and document tab; Guide centre (the "!" button) with every ta
- Export all: package ZIP now also holds the technical-office register, documents, tender, progress report, project pulse, calendar, asset register and an app-state backup. DWG cannot be written by a browser: the DXF files open in AutoCAD / BricsCAD and save as DWG.
- Logo: new T.O X wordmark (skewed grid, rounded-left T bar, tilted O, geometric X, gold triangle) following the user's reference picture; caption width matches the mark.

### In progress / needs checking
- (done) Reception-screen contour lines now fill the whole screen; ridge lines hide only a thin band under themselves.
- (done) Radio: Cairo and Saudi Quran streams verified to play (stream.radiojar.com ids 8s5u5tpdtwzuv and 0tpy1h0kxtzuv), Egyptian stations loaded from radio-browser.info, pop-out opens the stream itself in a small window. YouTube: embed no longer sends `no-referrer` (that caused the player error); fallback buttons "Pop-out vide
- Logo polish in the top bar at the compact density and on the splash screen.
- Live endpoints were not reachable from the build sandbox: Open-Meteo, NASA POWER, USGS, SoilGrids, mp3quran.net, Telegram, YouTube, Google. Code paths are mock-tested only.
- Shadows on the 3D model (heavy, not profiled), pop-out windows (browser may block), Notification reminders, WebRTC between two real devices.

### Still to do
- Plant-3D-style output with logos, render quality and a site-plan render.
- Video studio presets and resolutions; the explanation video (script is in `docs/VIDEO_SCRIPT.md`; a video file was not produced).
- Technicians and people figures, realistic site people and vehicles (currently off by default; do them well or remove).
- Coohom-like library (brands, colours, 360 panorama) and a project-type registry (towers, bridges, buildings, interiors).
- A small server for what a page cannot do: a Telegram bot that runs 24/7, reading the mailbox, Google Drive and Calendar sign-in (needs OAuth client ids), real permissions.
- Egyptian code (ECP) calculation methods; national seismic zone and wind maps as data; more engineering sheets (MEP, fire, drainage, irrigation).
- Mobile layout, accessibility pass, performance on very large models, Arabic proofreading of all new text.
- Decide when to publish: the deployed page (GitHub Pages) still shows the older build until the new one is pushed.


### Update 2026-11-19 (later): offline code-based simulation (`c_sim.js`)
The user asked for weather, wind, seismic and soil as code-based simulation, not internet data. Removed from the GIS tab: Open-Meteo wind archive, USGS earthquake list, NASA POWER, SoilGrids. Added, all offline:
- Wind: ASCE 7 method (SBC 301 follows it): Kz, qh, windward / leeward / side wall pressures with Gf and GCpi. Synthetic wind rose (Weibull, prevailing direction and spread, seeded). ECP 201 wind chapter NOT implemented.
- Seismic: ASCE 7 / SBC 301 spectrum and base shear (Fa, Fv default to the ASCE 7-10 tables, editable); Eurocode 8 form used by ECP 201 (ag, ground type, spectrum type 1 / 2, q, lower bound 0.2 ag, lambda 0.85). The EC8 reference spectrum parameters are the Eurocode 8 values; the ECP 201 edition in use may differ, so S, TB, TC, 
- Site class from Vs30 / SPT N / su (ASCE 7 and Eurocode 8 tables), liquefaction screening (simplified SPT: CSR, CRR, magnitude scaling, FS).
- Weather: synthetic year from user inputs (annual and daily temperature swing, sky clearness, Weibull wind) with exact sun position; monthly table, HDD / CDD, solar kWh/m2, PV yield estimate. It is a scenario, not recorded weather.
- To do next on this thread: add ECP 201 / SBC 301 national tables once the user supplies the edition (seismic zones, wind speeds, soil classes), Egyptian wind chapter, ECP soil and foundation chapters, ASHRAE-style design-day tables if wanted.


### Update 2026-11-19 (later): remove buttons and undo for placed items (`c_undo.js`)
- Tray at the bottom-left of the 3D view: one chip with × for each active section cut, each measurement, pending measure points, site cuts and the site plan, plus "Remove all". Ribbon Home → Edit has "Remove last placed item" and "Remove all cuts and measurements".
- Undo / redo (120 steps) now covers section cuts, measurements and site cuts: the view state is saved in every history step and inside the project file (`view` key). Before this, only parametric data was in the history, so undo did nothing for cuts and measures.
- Not covered: CAD window entities (they keep their own undo inside the CAD window), sheet callouts (edit them in the sheet notes).


### Update 2026-11-19 (later): new Radio and YouTube widgets (`c_media.js`)
- Radio widget: LCD display (station, status: connecting / on air / paused / no signal), play / pause, previous / next, tuning dial (slide through the stations of the current group), volume, groups Egypt / Saudi / Reciters / All, station list, auto fallback to a second stream URL, add your own stream URL, pop-out small window. S
- YouTube widget: search box and results with thumbnails; click plays inside the widget (youtube-nocookie embed, no account) or, in "my browser account" mode, opens YouTube in a small window. Search uses public Piped servers (api.piped.private.coffee worked; others are tried in turn); if all fail the page offers "Search in a You


### Update 2026-11-19 (late): media, logo, and the next big requests
Done:
- Media that does not stop (`c_media2.js`): the YouTube video lives in a floating widget outside every panel (drag the title to move, drag the bottom corner to resize, buttons for smaller / bigger / hide-picture-keep-sound / close; 120 px up to 640 px). A slim media bar (top of the page, movable to the bottom) holds radio and vi
- Ad skipping was NOT built (not possible from the page, and not something to build). Use a YouTube account without ads if needed.
- Logo: angular T.O X mark (T as a leaning "7", O as a leaning parallelogram ring with chamfers, X from two straight strokes, no triangle), tight spacing, same lean (38 degrees) for all, matches the reference picture's angles and proportions as closely as could be read from it.
To do next (owner's latest requests, not started):
1. Make each tool window imitate its source program exactly (AutoCAD for the CAD window: command line, ribbon Home groups Draw / Modify / Annotation / Layers / Block / Properties, status bar OSNAP / ORTHO / POLAR / GRID, model and layout tabs, black canvas, crosshair, ViewCube, wheel zoom and pan, window / crossing selection, gr
2. Animation and simulation controls (play, pause, disassemble, assemble, walk) need a professional pass; add a Rotate on/off option; make the site plan and display options easy to find in the Views menu.
3. Timeline playback must show an indicator: current activity name, highlight the matching row in the schedule table and scroll to it, highlight its dates, type, early / late start and finish and the critical path while it plays.


### Update 2026-11-19 (night): logo final and the next requests

1:# MEETING ROOM: agreements, decisions and status
8:## Decisions agreed with the owner
21:## Features built
25:## Validation status
31:## Open items
40:## 4D, safety, clashes, sharing, agents (added later)
55:## Project calculations received (amr.rar, 2026-11-19)
69:## Session log 2026-11-19: T.O X (Technical Office X) — what is done, what is running, what is left
72:### How to resume
78:### Done (headless-tested with mocks; real-browser and live-internet behaviour NOT verified)
91:### In progress / needs checking
98:### Still to do
109:### Update 2026-11-19 (later): offline code-based simulation (`c_sim.js`)
118:### Update 2026-11-19 (later): remove buttons and undo for placed items (`c_undo.js`)
124:### Update 2026-11-19 (later): new Radio and YouTube widgets (`c_media.js`)
129:### Update 2026-11-19 (late): media, logo, and the next big requests
140:### Update 2026-11-19 (night): logo final and the next requests
151:### 2026-11-19 (late): see docs/STATUS.md for the full done / not-done list.
154:### Update 2026-11-19 (night): Drive review
158:### Update 2026-11-19 (night): logo and render
163:### 2026-11-19 (end of day): hand-over notes before the conversation is compressed
170:### 2026-11-19 (last): lobby and pending list at the moment of compression
180:## Backlog after owner review 2026-11-19 (nothing below is built yet unless marked)
197:## Owner decisions 2026-11-19 (late)
203:## Plan additions 2026-11-19 (owner)
210:## 2026-11-19 pm
216:## Simulation audit 2026-11-19
223:## Adhan and calculation checks 2026-11-19
227:## Program shells 2026-11-20
Shell cwd was reset to /Users/M7/Documents/ai-trading-dashboard
```

</details>

### assistant · 2026-11-20T06:45:37.379Z

**أداة:** `ToolSearch`

```json
{
 "query": "select:WebSearch,SendMessage",
 "max_results": 3
}
```

### user · 2026-11-20T06:45:37.594Z

**نتيجة أداة:**
```

```

### assistant · 2026-11-20T06:45:39.845Z

Reading is done. I'm now running web searches to verify pricing and openness for each system, then I'll write `COMPARE_SYSTEMS.md`.

### assistant · 2026-11-20T06:45:40.188Z

**أداة:** `WebSearch`

```json
{
 "query": "Autodesk Revit subscription price per year Autodesk Build ACC pricing",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:40.538Z

**أداة:** `WebSearch`

```json
{
 "query": "Trimble Connect pricing plans free Personal Business Business Premium",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:40.989Z

**أداة:** `WebSearch`

```json
{
 "query": "Procore pricing model annual construction volume unlimited users",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:41.520Z

**أداة:** `WebSearch`

```json
{
 "query": "Speckle pricing free tier Community plan viewer open source licence",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:41.857Z

**أداة:** `WebSearch`

```json
{
 "query": "Solibri pricing licence Solibri Office model checking",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:42.378Z

**أداة:** `WebSearch`

```json
{
 "query": "Archicad BIMcloud pricing subscription Graphisoft Solo Collaborate",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:42.930Z

**أداة:** `WebSearch`

```json
{
 "query": "Microsoft Project plan 1 plan 3 plan 5 price per user month Planner",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:43.357Z

**أداة:** `WebSearch`

```json
{
 "query": "Arcol Snaptrude Hypar Testfit Autodesk Forma pricing AI building design",
 "mode": "standard"
}
```

### user · 2026-11-20T06:45:48.701Z

<details><summary>نتيجة أداة (2979 حرف)</summary>

```
Web search results for query: "Procore pricing model annual construction volume unlimited users"

Links: [{"title":"procore.com","url":"https://procore.com/pricing"},{"title":"www.procore.com","url":"https://www.procore.com/sem/pricing"},{"title":"www.procore.com","url":"https://www.procore.com/en-ca/pricing"},{"title":"• Skip to main content","url":"https://www.procore.com/jobsite/understanding-procores-pricing-model"},{"title":"Pricing Overview for Procore","url":"https://www.trustradius.com/products/procore/pricing"},{"title":"www.procore.com","url":"https://www.procore.com/en-au/pricing"},{"title":"Procore Pricing Explained: Cost, Contracts, Licensing and Alternatives","url":"https://www.larksuite.com/blog/procore-pricing"},{"title":"Procore Pricing Explained: Cost, Contracts, Licensing and Alternatives","url":"https://www.larksuite.com/en_us/blog/procore-pricing"},{"title":"Procore Pricing: Real Costs, Plans, and Whether It's Worth It in 2026","url":"https://www.getonecrew.com/post/procore-pricing"},{"title":"Enterprise DNA","url":"https://enterprisedna.co/omni/instead-of/procore/pricing"},{"title":"Procore Company LogoRequest a DemoLog In","url":"https://www.procore.com/en-ae/pricing"},{"title":"vertice.one","url":"https://www.vertice.one/vendors/procore"},{"title":"tekpon.com","url":"https://tekpon.com/software/procore/pricing"},{"title":"procore pricing analysis 2026","url":"https://projul.com/blog/procore-pricing-analysis-2026/"},{"title":"connecteam.com","url":"https://connecteam.com/reviews/procore/"},{"title":"New for owners: Capital portfolio management capabilities with built-in AI","url":"https://www.procore.com/?r=jcs"},{"title":"Making Procore Pricing More Flexible and Predictable","url":"https://blog.procore.com/deal-structures"},{"title":"zoftwarehub.com","url":"https://zoftwarehub.com/en-sa/products/procore/pricing"}]

Procore prices by Annual Construction Volume (ACV) and doesn't publish a rate card. Its official pricing page says pricing depends on the products you need and the amount of construction you do. It charges an upfront annual fee by product, based on ACV, the aggregate dollar value of the construction work across your projects.

Unlimited users are included. Users can include employees as well as clients, subcontractors, and vendors. Unlimited data storage and support are bundled into the contract as well, at no additional cost.

Third-party price estimates vary widely. One source puts common annual costs between $15,000 and $80,000 before implementation. Another estimates $100,000 - $600,000+/yr for large contractors ($250M+). These are unofficial, so confirm figures with Procore sales. One source also notes that annual price increases of 5–14% at renewal are reported, though Procore's own materials promise predictable budgeting for the year, without unexpected price increases along the way.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:49.100Z

<details><summary>نتيجة أداة (3515 حرف)</summary>

```
Web search results for query: "Microsoft Project plan 1 plan 3 plan 5 price per user month Planner"

Links: [{"title":"microsoft project pricing","url":"https://thedigitalprojectmanager.com/tools/microsoft-project-pricing"},{"title":"Microsoft Project Review and Pricing Guide","url":"https://tech.co/project-management-software/microsoft-project-review"},{"title":"how much does microsoft project project cost 86d84b6dfded","url":"https://medium.com/@softwarelegit/how-much-does-microsoft-project-project-cost-86d84b6dfded"},{"title":"microsoft project hinnoittelu","url":"https://thedigitalprojectmanager.com/fi/tools/microsoft-project-hinnoittelu/"},{"title":"Free Trial","url":"https://www.saasworthy.com/product/microsoft-ppm/pricing"},{"title":"This is the Trace Id: 82504f634ee465c11a7d25e0ea2efef6","url":"https://www.microsoft.com/en-in/microsoft-365/project/project-plan-5"},{"title":"Close Menu","url":"https://www.saasworthy.com/blog/?p=20127"},{"title":"This is the Trace Id: e0027924cc6a1717f2d595726f38e75f","url":"https://www.microsoft.com/en-in/microsoft-365/planner/project-plan-5"},{"title":"prisnivaer og kostnader for microsoft project","url":"https://thedigitalprojectmanager.com/nb/tools/prisnivaer-og-kostnader-for-microsoft-project/"},{"title":"how to choose a microsoft project plan and understand its cost","url":"https://androidexperto.com/how-to-choose-a-microsoft-project-plan-and-understand-its-cost/"},{"title":"Microsoft Project & Portfolio Management Preisübersicht","url":"https://www.g2.com/de/products/microsoft-microsoft-project-portfolio-management/pricing"},{"title":"Microsoft Project Pricing Plans & Costs Guide","url":"https://projectmanagers.net/?p=22496"},{"title":"This is the Trace Id: 3c03ff53ce67d9445aa5b8d0f77dae4e","url":"https://www.microsoft.com/en-sg/microsoft-365/project/project-plan-5"},{"title":"Back to ArticlesBack","url":"https://mpug.com/cloudy-conditions-clarifying-ms-projects-plans-and-pricing-structures"},{"title":"Microsoft Project Plans Pricing","url":"https://apis.io/plans/microsoft-project/microsoft-project-plans-pricing/"},{"title":"Trace Id is missing","url":"https://products.office.com/en-gb/project/project-online-professional"}]

Across the results, the per-user monthly prices are consistent: Planner Plan 1 is $10, Planner and Project Plan 3 is $30, and Planner and Project Plan 5 is $55. Most sources note annual billing.

- **Plan 1 ($10):** One source lists it at $10 per user per month with annual billing on Microsoft's U.S. comparison page. Microsoft's Singapore page shows USD$10.00 user/month, paid yearly.
- **Plan 3 ($30):** Plan 3 costs $30 per user per month with annual billing, according to the same source. Microsoft's Singapore page lists it at USD$30.00 user/month, paid yearly.
- **Plan 5 ($55):** Multiple sources list it at $55 per user per month. One source adds that Microsoft's comparison page says new purchases ended after May 1, 2026. That is the only source for this claim, so verify it on Microsoft's site before relying on it.

Some secondary sites list a free Planner tier, but the sources don't consistently agree on whether Planner is free. One says Planner Plan 1 is the first paid tier, and another says No free plan is available. Prices vary by region and currency, and the Indian rupee and British pound pages show different figures. Check Microsoft's official pricing page for current figures.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:49.192Z

<details><summary>نتيجة أداة (3253 حرف)</summary>

```
Web search results for query: "Trimble Connect pricing plans free Personal Business Business Premium"

Links: [{"title":"subscription plans","url":"https://geospatial.trimble.com/en/products/software/trimble-connect/subscription-plans"},{"title":"connect.trimble.com","url":"https://connect.trimble.com/node/351"},{"title":"stg-connect.trimble.com","url":"https://stg-connect.trimble.com/node/351"},{"title":"trimble connect","url":"https://www.capterra.co.uk/software/208909/trimble-connect"},{"title":"Trimble Connect","url":"https://www.softwareadvice.com/construction/trimble-connect-profile/"},{"title":"trimble connect","url":"https://www.capterra.ie/software/208909/trimble-connect"},{"title":"trimble connect","url":"https://www.capterra.ca/software/208909/trimble-connect"},{"title":"trimble connect","url":"https://www.capterra.ca/reviews/208909/trimble-connect"},{"title":"Trimble Connect Knowledge Center","url":"https://community.trimble.com/blogs/lindsay-renkel/2025/05/05/trimble-connect-new-pro-and-innovate-plans-faq"},{"title":"trimble connect","url":"https://www.capterra.in/software/208909/trimble-connect"},{"title":"trimble connect","url":"https://www.capterra.com.au/software/208909/trimble-connect"},{"title":"www.spotsaas.com","url":"https://www.spotsaas.com/product/trimble-connect/pricing"},{"title":"trimble connect","url":"https://www.capterra.com.sg/reviews/208909/trimble-connect"},{"title":"trimble connect","url":"https://www.capterra.co.nz/software/208909/trimble-connect"},{"title":"trimble connect","url":"https://www.softwareadvice.co.uk/software/405096/trimble-connect"},{"title":"trimble connect","url":"https://www.getapp.co.uk/software/2030995/trimble-connect"},{"title":"trimble connect","url":"https://www.saasworthy.com/product/trimble-connect"}]

The search turned up a mix of current and outdated information, and the names may have changed.

- **Personal (free):** The official Trimble page lists a free tier. A Trimble community post says it includes one project, invitations for up to five members, and 10 GB of storage. Personal users can also join up to five business projects, with read-only access to projects beyond that.
- **Business:** Third-party listings give conflicting prices. Capterra lists $10/month per user, while SaaSworthy's listing, last updated in 2020, shows $100 billed yearly. Business adds unlimited projects, members, and data.
- **Business Premium:** The official Trimble page shows $23.95 per user per month, billed annually. Capterra lists $250 per user per year. Business Premium adds advanced BIM tools, enriched 3D workflows, and access to apps and extensions.
- **Plan changes:** A Trimble community post says that as of May 20, 2025, the Pro and Innovate plans replaced Business and Business Premium for new web purchases and renewals. Existing Business and Business Premium subscriptions bought through sales reps or resellers were not changed.

The official Trimble pages are the most reliable source here, but they appear to be partly out of date. Pricing also varies by region, so confirm current figures with Trimble or a local distributor before relying on them.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:49.909Z

<details><summary>نتيجة أداة (6377 حرف)</summary>

```
Web search results for query: "Speckle pricing free tier Community plan viewer open source licence"

Links: [{"title":"Company news","url":"https://speckle.systems/blog/projects-get-a-new-home-and-pricing-plans"},{"title":"speckle.systems","url":"https://speckle.systems/pricing/"},{"title":"> ## Documentation Index","url":"https://docs.speckle.systems/workspaces/new-plans-faq.md"},{"title":"new plans faq","url":"https://docs.speckle.systems/workspaces/new-plans-faq"},{"title":"v1.speckle.systems","url":"https://v1.speckle.systems/pricing"},{"title":"speckle announces project and usage based plans","url":"https://osarch.org/2026/01/21/speckle-announces-project-and-usage-based-plans/"},{"title":"Speckle Pricing Overview","url":"https://www.g2.com/products/speckle/pricing"},{"title":"docs.speckle.systems","url":"https://docs.speckle.systems/workspaces/billing"},{"title":"Plans and Trials","url":"https://support-and-docs.gitbook.io/speckel-docs/basics/get-support/faqs/plans-and-trials"},{"title":"Can no longer use more than 5 models in free and weird price increase","url":"https://speckle.community/t/can-no-longer-use-more-than-5-models-in-free-and-weird-price-increase/17659"},{"title":"Community Plan","url":"https://support-and-docs.gitbook.io/speckel-docs/~/changes/mJhergSECXb5YAl5MO9D/the-basics/our-plans/community-plan"},{"title":"gitbook.io","url":"https://support-and-docs.gitbook.io/speckel-docs/basics/get-started/plans"},{"title":"PSA: New business model","url":"https://speckle.community/t/psa-new-business-model/21591"},{"title":"meta.discourse.org","url":"https://meta.discourse.org/t/why-are-you-able-to-offer-a-free-plan/404699/4?tl=en"},{"title":"Speckle Workspaces: Out of Beta, Into Action","url":"https://speckle.community/t/speckle-workspaces-out-of-beta-into-action/15393"},{"title":"Please don't take my demo models hostage 😢","url":"https://speckle.community/t/please-dont-take-my-demo-models-hostage/21687"},{"title":"our plans","url":"https://support-and-docs.gitbook.io/speckel-docs/~/changes/mJhergSECXb5YAl5MO9D/the-basics/our-plans"},{"title":"dbaad893 838f 4a8b 91b8 a1f4f5866af3","url":"https://marketplace.autodesk.com/publisher-profile/dbaad893-838f-4a8b-91b8-a1f4f5866af3"},{"title":"Authorization for commercial use","url":"https://speckle.community/t/authorization-for-commercial-use/10281"},{"title":"au.linkedin.com","url":"https://au.linkedin.com/in/clistix"}]

Links: [{"title":"github.com","url":"https://github.com/didimitrie/future.speckle"},{"title":"# The Speckle Viewer","url":"https://cdn.jsdelivr.net/npm/@speckle/[REDACTED_EMAIL]/readme.md"},{"title":"alternativeto.net","url":"https://alternativeto.net/software/speckle/about"},{"title":"docs.speckle.systems","url":"https://docs.speckle.systems/developers/viewer/"},{"title":"exflgitlab02.desy.de","url":"https://exflgitlab02.desy.de/dataAnalysis/extra-speckle/-/blob/master/LICENSE"},{"title":"4 minute read","url":"https://issuu.com/augi/docs/aw202307hr/s/27690791"},{"title":"opensource.construction","url":"https://opensource.construction/projects/speckle/"},{"title":"> ## Documentation Index","url":"https://docs.speckle.systems/developers/viewer/introduction.md"},{"title":"skypack.dev","url":"https://www.skypack.dev/view/@speckle/viewer"},{"title":"Last Updated: Feb 22, 2022","url":"https://speckle.systems/eula/"},{"title":"Open Source in AEC & Speckle","url":"https://speckle.systems/blog/opensource-aec-speckle"},{"title":"speckle viewer","url":"https://www.npmjs.com/package/@speckle/speckle-viewer"},{"title":"Company news","url":"https://speckle.systems/blog/how-to-make-the-most-out-of-the-speckle-viewer/"},{"title":"Speckle Blog / Open Source in AEC & Speckle","url":"https://speckle.community/t/speckle-blog-open-source-in-aec-speckle/1047"},{"title":"source-hub.etos-pro.ru","url":"https://source-hub.etos-pro.ru/specklesystems/speckle-server/src/commit/628fac0be0b13885d445ce66e569798b948c4720"},{"title":"github.com%2Fspecklesystems%2Fspeckle server","url":"https://awesome.ecosyste.ms/projects/github.com%2Fspecklesystems%2Fspeckle-server"},{"title":"Open Source in AEC & Speckle","url":"https://v1.speckle.systems/blog/opensource-aec-speckle"},{"title":"speckle server","url":"https://github-users.yhajoa.workers.dev/homebound-team/speckle-server"},{"title":"Masquer le sommaire","url":"https://help.solidworks.com/2026/french/DSSWXComposerDoc/FrontmatterSWXComposer/DSSWXComposerLegalNotices.htm"}]

The current free tier is called **Explore**, not "Community." The "Community" plan in the search results belongs to an unrelated product.

**Free tier (current):** Explore is free for teams of up to 10 users on one project. It includes 30-day version history, one Speckle Intelligence dashboard, up to 100 total versions, and up to 50 monthly syncs. Explore is our free plan for teams of up to 10 users working on 1 project. It includes a 30-day version history, one Speckle Intelligence dashboard, up to 100 total versions, and up to 50 monthly syncs. Paid usage is based on syncs and versions, and a sync occurs whenever a new model version is created or when a productive receive occurs.

**Viewer licence:** The Speckle viewer is open source. The docs say Speckle has made the Speckle viewer available as an Open Source project and freely available component which you can use within your own code or website. The main repository, speckle-server, which includes the viewer package, is licensed under the Apache-2.0 License. The Speckle site also says Speckle uses the Apache License 2.0.

**Self-hosting:** Per the company's June 2025 announcement, self-hosted Speckle remains 100% free and open-source. Workspace perks such as security automation are only on the hosted version.

**Caveats:**
- Pricing has changed several times. A January 2026 post reports that the changes apply to hosted commercial plans, not to self-hosting. Legacy Starter and Business plans are retiring, and the older 2022 EULA page may be out of date.
- The GitBook "Community Plan" pages refer to a different product (Speckel, a building-assessment tool), so I didn't use them for Speckle's free tier.
- I didn't find a clear answer on whether commercial use of the free tier is allowed. A forum question on that topic was unresolved in the results.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:50.060Z

<details><summary>نتيجة أداة (3916 حرف)</summary>

```
Web search results for query: "Archicad BIMcloud pricing subscription Graphisoft Solo Collaborate"

Links: [{"title":"Plans & pricing","url":"https://graphisoft.com/buy-now"},{"title":"archicad collaborate","url":"https://www.graphisoft.com/ie/plans-and-products/archicad-collaborate"},{"title":"Plans & pricing","url":"https://graphisoft.com/ie/buy-now"},{"title":"Plans & pricing","url":"https://graphisoft.com/uk/buy-now"},{"title":"Plans & pricing","url":"https://graphisoft.com/hk/buy-now"},{"title":"Plans & pricing","url":"https://www.graphisoft.com/?p=81162"},{"title":"graphisoft intros new archicad collaborate subscription offering","url":"https://architosh.com/2023/03/graphisoft-intros-new-archicad-collaborate-subscription-offering/"},{"title":"How Much Does ArchiCAD Cost? Pricing Explained","url":"https://www.scan2cad.com/blog/cad/archicad-pricing/"},{"title":"Select license type","url":"https://graphisoft.com/buy-now/select-license-type"},{"title":"Archicad Collaborate","url":"https://graphisoft.com/plans-and-products/archicad-collaborate"},{"title":"Sphere, Morph","url":"https://graphisoft.com/plans-and-products/archicad-studio"},{"title":"buy now","url":"https://graphisoft.com/my/buy-now"},{"title":"architosh.com","url":"https://architosh.com/2023/03/graphisoft-intros-new-archicad-collaborate-subscription-offering/amp"},{"title":"www.graphisoft.com","url":"https://www.graphisoft.com/?p=72840"},{"title":"graphisofts archicad collaborate makes leading bim technology more accessible through new subscription offering","url":"https://newsroom.graphisoft.com/graphisofts-archicad-collaborate-makes-leading-bim-technology-more-accessible-through-new-subscription-offering.json"},{"title":"Continue your","url":"https://www.graphisoft.com/?p=79177"},{"title":"graphisoft launches archicad studio subscription plan","url":"https://architosh.com/2025/03/graphisoft-launches-archicad-studio-subscription-plan/"}]

Graphisoft's pricing varies by region and plan, and the search results are a mix of current and older pages.

- **Current plan names:** Archicad Studio was launched in 2025 for solo practitioners and small teams, and it uses BIMcloud Basic for local teamwork. Graphisoft currently offers two subscription plans: Archicad Studio and Archicad Collaborate. The main differences are in the Teamwork features. Archicad Studio uses BIMcloud Basic, while Archicad Collaborate provides BIMcloud Software-as-a-Service (SaaS).
- **Archicad Solo:** Some pages still list Solo. In one, the Archicad Solo plan starts from €148 + tax / month on a 1-year term. Another regional page lists Archicad Solo at US$200 + tax / month with annual billing. A third page, which may predate the Studio rebrand, lists Archicad Studio, Archicad Collaborate, Archicad Max, MEP Designer Studio, and BIMcloud with monthly prices.
- **Collaborate:** One US page shows Collaborate at $406 + tax / month, while a regional page lists Archicad Collaborate at US$234.17 + tax / month with annual billing. Prices differ by source and date, so check the official store for your billing country.
- **Standalone BIMcloud:** Regional pages show it separately. One lists BIMcloud starting from US$45, and another lists BIMcloud at $99 + tax / month.
- **Solo vs. Collaborate:** Solo does not include BIMcloud. An older analysis states that the ArchiCAD Solo offering only gives access to the ArchiCAD BIM software; it does not come with BIMx or BIMcloud capabilities.
- **Terms:** Plans are generally sold per seat with monthly or annual billing, and some offer multi-year price locks. The Graphisoft store notes that prices are for information only, and the final price depends on your billing country.

For current figures, check graphisoft.com/buy-now for your country, since the cached pages above are inconsistent.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:50.365Z

<details><summary>نتيجة أداة (3848 حرف)</summary>

```
Web search results for query: "Arcol Snaptrude Hypar Testfit Autodesk Forma pricing AI building design"

Links: [{"title":"snaptrude alternatives","url":"https://www.nomic.ai/compare/snaptrude-alternatives"},{"title":"Best AI Tools for Architects in 2026: 14 Tools for Design, Feasibility, and Presentations","url":"https://resources.rework.com/tools/ai-tools/best-ai-tools-for-architects-2026"},{"title":"Autodesk: beyond the seat, the meter","url":"https://aecmag.com/ai/autodesk-beyond-the-seat-the-meter/"},{"title":"2026年版 建築家におすすめのAIツール14選:設計・実現可能性検証・プレゼンテーション","url":"https://resources.rework.com/ja/tools/ai-tools/best-ai-tools-for-architects-2026"},{"title":"July 15, 2025","url":"https://www.snaptrude.com/blog/top-10-best-architecture-design-software-in-2025"},{"title":"AEC September / October 25","url":"https://issuu.com/x3dmedia/docs/aec_september_october_25"},{"title":"arkdesign alternatives","url":"https://www.nomic.ai/compare/arkdesign-alternatives"},{"title":"Forma for Buildings","url":"https://www.autodesk.com/au/products/forma-for-buildings/overview"},{"title":"Forma for Buildings","url":"https://www.autodesk.com/eu/products/forma-for-buildings/overview"},{"title":"Buy Forma for Buildings","url":"https://www.autodesk.com/au/products/forma-for-buildings/buy"},{"title":"Industrials / Construction Tech","url":"https://www.cbinsights.com/esp/industrials/construction-tech/generative-ai-%E2%80%94-architectural-design"},{"title":"a new center of gravity arcol is rebuilding architectural authoring","url":"https://architosh.com/2026/01/a-new-center-of-gravity-arcol-is-rebuilding-architectural-authoring/"},{"title":"Melhores Ferramentas de IA para Arquitetos em 2026: 14 Ferramentas para Design, Viabilidade e Apresentações","url":"https://resources.rework.com/pt/tools/ai-tools/best-ai-tools-for-architects-2026"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/?p=56350"},{"title":"adsknews.autodesk.com","url":"https://adsknews.autodesk.com/en/wp-json/wp/v2/news/56350"},{"title":"aecmag.com","url":"https://aecmag.com/search/revit/page/22/"},{"title":"Best AI Tools for Architects 2026","url":"https://awesomeagents.ai/tools/best-ai-tools-for-architects-2026/"}]

The search turned up mostly third-party roundups, and their prices often conflict, so verify against vendor sites before relying on them.

- **Autodesk Forma:** Autodesk's Forma Building Design is free for Revit subscribers, while Forma Site Design is about $185/month standalone according to third-party trackers. Full standalone pricing requires a quote. Another roundup lists it at from ~$400/month (often via the AEC Collection), and a different one puts it at Freemium — from ~$50/user/month. Autodesk says Forma Building Design is available now for all Revit and AEC Collection subscribers.
- **Arcol:** Listed as freemium with paid plans that scale by team. One source describes it as AI-assisted design and integrated project metrics.
- **Snaptrude:** One roundup gives $499/year per user and a free option for 3 projects. Note that its listing is a third-party aggregator, not Snaptrude's own page.
- **TestFit:** Pricing is reported as From ~$250/user/month in one source and $100/month in another.
- **Hypar:** A free tier exists, but paid pricing on request, with no public pricing for paid tiers.

The sources also differ in framing. One piece says Autodesk is betting that customers will continue investing in Revit while Autodesk spends the next few years building Forma into a credible alternative, and a critical Arcol interview says that because Forma is bundled with Autodesk subscriptions, many customers have access to it for free but still choose Arcol for its speed, immediacy, and collaborative depth.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:50.379Z

<details><summary>نتيجة أداة (3564 حرف)</summary>

```
Web search results for query: "Autodesk Revit subscription price per year Autodesk Build ACC pricing"

Links: [{"title":"Frequently Asked Questions","url":"https://www.autodesk.com/solutions/revit-subscription-faq"},{"title":"# Revit Pricing: A Comprehensive Guide | Capterra","url":"https://www.capterra.com/p/265023/Revit/pricing/"},{"title":"autodesk revit drops to 399 for a year","url":"https://www.pcworld.com/article/3224965/autodesk-revit-drops-to-399-for-a-year.html"},{"title":"Design and make anything with Autodesk software","url":"https://www.autodesk.com/store"},{"title":"Design and make anything with Autodesk software","url":"https://www.autodesk.com/asean/products"},{"title":"Design and make anything with Autodesk software","url":"https://www.autodesk.com/ae/products"},{"title":"Design and make anything with Autodesk software","url":"https://www.autodesk.com/asean/products?panel=buy"},{"title":"www.scan2cad.com","url":"https://www.scan2cad.com/blog/?p=36097"},{"title":"Revit Pricing in 2026: Plans, Costs & Is It Worth It?","url":"https://www.myarchitectai.com/blog/revit-pricing"},{"title":"Frequently Asked Questions","url":"https://dotcom-aem.efddotcom-stg.autodesk.com/solutions/revit-subscription-faq"},{"title":"Frequently Asked Questions","url":"https://www-pt.autodesk.com/solutions/revit-subscription-faq"},{"title":"Design and make anything with Autodesk software","url":"https://www.autodesk.com/buy"},{"title":"Revit Cost","url":"https://www.nobledesktop.com/learn/revit/revit-cost"},{"title":"revit cost","url":"https://blog.nobledesktop.com/learn/revit/revit-cost"},{"title":"Architecture, Engineering & Construction Collection","url":"https://www.autodesk.com/collections/architecture-engineering-construction/architects?term=1-YEAR"}]

The search returned solid Revit pricing but nothing specific to Autodesk Build or Autodesk Construction Cloud (ACC) pricing.

**Revit (official Autodesk FAQ):** The official FAQ puts a standard subscription at $380 monthly, $3,005 annually, or $9,020 for a 3-year term. The Standard plan is included with every Revit subscription and can be purchased on a monthly, annual, or 3-year basis. Medium, large, and extra-large teams can contact Autodesk or an authorized reseller to explore subscription options.

**Conflicting figures:** Third-party sources list older or different numbers. Capterra gives $365 per user per month, and $2,910 per user per year on the Annual plan. Noble Desktop gives similar figures and a $8,730 three-year price. A sponsored deal listing shows a 1-year subscription for $399 (MSRP $3,005), but that is a reseller promotion, and prices may have changed since it was posted. The Autodesk store listing shows a Revit price of $2,010/year, which is probably a regional or promotional price, so I'd treat it with caution.

**Flex:** Pay-as-you-go tokens are another option. Flex is $300 per 100 tokens (minimum), and Revit uses 10 tokens per day.

**AEC Collection:** Autodesk's bundle that includes Revit is listed at $3,675 annually and $460 monthly, with a 3-year price of $11,030.

**Autodesk Build / ACC:** I found no pricing for these. Autodesk's store lists Forma Build Essentials at $800/year, but that is a separate product, not Autodesk Build or ACC. Other Autodesk products on the store show "Contact Autodesk for pricing." A follow-up search aimed at "Autodesk Construction Cloud pricing" or "Autodesk Build plans" would be needed to fill this gap.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:45:50.591Z

<details><summary>نتيجة أداة (3741 حرف)</summary>

```
Web search results for query: "Solibri pricing licence Solibri Office model checking"

Links: [{"title":"www.selecthub.com","url":"https://www.selecthub.com/p/building-information-modeling-software/solibri/"},{"title":"Solibri Office","url":"https://www.trustradius.com/compare-products/solibri-office"},{"title":"36419217316119 What s the difference between a Solibri Subscription and a Solibri perpetual license","url":"https://help.solibri.com/hc/en-us/articles/36419217316119-What-s-the-difference-between-a-Solibri-Subscription-and-a-Solibri-perpetual-license"},{"title":"Solibri Office Pricing","url":"https://www.trustradius.com/products/solibri-office/pricing"},{"title":"europeanpurpose.com","url":"https://europeanpurpose.com/tool/solibri"},{"title":"store.solibri.com","url":"https://store.solibri.com/"},{"title":"5,000 tokens","url":"https://store.solibri.com/en"},{"title":"solibri office","url":"https://us.fitgap.com/products/055134/solibri-office"},{"title":"www.solibri.com","url":"https://www.solibri.com/pricing"},{"title":"our offering","url":"https://www.solibri.com/our-offering"},{"title":"www.solibri.com","url":"https://www.solibri.com/tokens"},{"title":"TrustRadius: an HG Insights company","url":"https://www.trustradius.com/products/solibri-office/details"},{"title":"Solibri Premium","url":"https://www.aecplustech.com/tools/solibri-premium"},{"title":"Solibri Starter","url":"https://www.aecplustech.com/tools/solibri-starter"},{"title":"PCP 0678 6258","url":"https://platform.softwareone.com/product/solibri-office/PCP-0678-6258"},{"title":"solibri office","url":"https://solibri.com/solibri-office"},{"title":"🎓 New courses are launching soon! Get early updates and freebies — Subscribe here","url":"https://archgyan.com/?p=12710"},{"title":"# Solibri Office Reviews","url":"https://www.g2.com/products/solibri-office/reviews"},{"title":"www.nordicbim.com","url":"https://www.nordicbim.com/en/products/solibri"},{"title":"Solibri's New Product Family","url":"https://aecbytes.com/newsletter/2019/issue_100.html"}]

Solibri pricing varies a lot by source, and the official pricing page wasn't in the results, so verify current figures with Solibri before budgeting.

- **Third-party listings (USD, Solibri Office):** TrustRadius lists an Individual Monthly Subscription at $149 per month per user and an Individual Annual Subscription at $1200 per year per user. SelectHub gives a different figure, starting at $185 (Per User, Monthly).
- **Euro pricing:** FitGap shows pricing from €1,870 per license per year.
- **Tiered plans (Solibri Store, per year per licence, EUR):** One listing gives EUR 99 for Starter, EUR 1,428 for Essential, EUR 2,109 for Advanced and EUR 2,772 for Premium. Another says the Starter tier is $99 per year for a named license, sold through the Solibri Store. Premium is the only tier with Superrun, a new way to automate model checking in Solibri.
- **Licence types:** Named licenses are for specific users, while concurrent licenses let teams share access. Subscriptions for Solibri Office are available as an individual subscription for single user (billed monthly or annually) and as a subscription seat.
- **Tokens:** Autorun runs are billed through tokens, but if you have a Solibri Office license, you don't need to use tokens for Autorun.
- **Older figure:** An AECbytes article from 2019 cites a small upfront investment (130€ per month). It is outdated.

Solibri Office is described as a model checking and collaboration solution that imports building models from BIM software by using the standardized IFC interface. A free trial is available according to TrustRadius.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-20T06:45:52.929Z

**أداة:** `WebSearch`

```json
{
 "query": "Bentley OpenBuildings Designer ProjectWise subscription pricing virtuoso subscription",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:53.427Z

**أداة:** `WebSearch`

```json
{
 "query": "Oracle Primavera Cloud pricing per user P6 Professional price Navisworks Manage price per year",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:54.139Z

**أداة:** `WebSearch`

```json
{
 "query": "Bonsai BIM IfcOpenShell licence GPL FreeCAD LGPL BIM workbench That Open Engine licence MIT",
 "mode": "standard"
}
```

### assistant · 2026-11-20T06:45:54.837Z

**أداة:** `WebSearch`

```json
{
 "query": "QGIS licence GPL ArcGIS Pro pricing per year ArcGIS Online named user; Coohom pricing; SketchUp pricing Go Pro Studio",
 "mode": "standard"
}
```

### user · 2026-11-20T06:46:01.508Z

<details><summary>نتيجة أداة (2472 حرف)</summary>

```
Web search results for query: "Bonsai BIM IfcOpenShell licence GPL FreeCAD LGPL BIM workbench That Open Engine licence MIT"

Links: [{"title":"dev.opencascade.org","url":"https://dev.opencascade.org/project/ifcopenshell"},{"title":"wiki.freecad.org","url":"https://wiki.freecad.org/IfcOpenShell"},{"title":"wiki.freecad.org","url":"https://wiki.freecad.org/IfcOpenShell/it"},{"title":"About License","url":"https://www.github.com/IfcOpenShell/IfcOpenShell/discussions/4102"},{"title":"IfcOpenShell is a library to support the IFC file format","url":"https://anaconda.org/freecad/ifcopenshell"},{"title":"wiki.osarch.org","url":"https://wiki.osarch.org/ifcopenshell/"},{"title":"wiki.osarch.org","url":"https://wiki.osarch.org/index.php/IfcOpenShell"},{"title":"github.com","url":"https://github.com/3drepo/IfcOpenShell"},{"title":"github.com","url":"https://github.com/aothms/IfcOpenShell"},{"title":"github.com","url":"https://github.com/pitmanmw/IfcOpenShell"}]

The search covered the IfcOpenShell licensing and the Bonsai add-on, but it returned nothing on That Open Engine's MIT licence or the licence of FreeCAD's BIM workbench.

- **IfcOpenShell core:** Its main library is LGPL. One source describes it as an open source (LGPL) software library for working with IFC format. The IfcOpenShell repository lists its Python package and most internal libraries under LGPL-3.0-or-later.
- **Bonsai (the Blender add-on, formerly BlenderBIM):** The same repository listing gives its licence as GPL-3.0-or-later. That is a separate component from the LGPL libraries. An older wiki entry notes that IfcBlender Replaced by Bonsai.
- **Mixed licensing in one project:** A GitHub discussion covering IfcConvert says that IfcConvert is LGPL v3-or-later licensed, not GPL v3. A developer there asked whether an MIT-licensed SDK would need to be GPLv3, and the thread's answer is not in the results. The search also turned up no answer on whether linking LGPL components from an MIT project is permitted.
- **FreeCAD:** The FreeCAD wiki says that as of v0.19, FreeCAD is able to import IFC files as long as the ifcopenshell Python module is available in the system. It does not state the BIM workbench's own licence.

Since this is a legal question, the GitHub thread and the LGPL/GPL texts should be checked directly, and a lawyer should confirm the MIT-compatibility question.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:46:02.289Z

<details><summary>نتيجة أداة (3345 حرف)</summary>

```
Web search results for query: "Oracle Primavera Cloud pricing per user P6 Professional price Navisworks Manage price per year"

Links: [{"title":"What Is Oracle Primavera P6? Uses, Features & Pricing","url":"https://www.projectmanager.com/?p=54758"},{"title":"autodesk.com","url":"https://autodesk.com/products/navisworks/compare"},{"title":"Navisworks: 3D model review, coordination, and clash detection","url":"https://www.autodesk.com/products/navisworks/overview.takeover"},{"title":"top of page","url":"https://www.projectmanagertemplate.com/post/primavera-p6-software-cost-understanding-pricing"},{"title":"Navisworks: 3D model review, co-ordination and clash detection","url":"https://www.autodesk.com/in/products/navisworks/overview"},{"title":"Navisworks: 3D model review, coordination, and clash detection","url":"https://autodesk.com/navisworks"},{"title":"Navisworks: 3D model review, co-ordination and clash detection","url":"https://www.autodesk.com/in/products/navisworks"},{"title":"Navisworks: 3D model review, co-ordination and clash detection","url":"https://www.autodesk.com/in/products/navisworks/overview?plc=NAVMAN"},{"title":"www.autodesk.com","url":"https://www.autodesk.com/pl/products/navisworks"},{"title":"Navisworks: 3D model review, co-ordination and clash detection","url":"https://www.autodesk.com/au/products/Navisworks/overview"},{"title":"Navisworks: 3D model review, co-ordination and clash detection","url":"https://autodesk.com/au/products/navisworks?panel=buy"},{"title":"What Is Oracle Primavera P6? Uses, Features & Pricing","url":"https://www.projectmanager.com/blog/what-is-primavera-p6"},{"title":"how much does primavera p6 cost","url":"https://tensix.com/how-much-does-primavera-p6-cost/"},{"title":"Free Trial","url":"https://www.saasworthy.com/product/navisworks/pricing"},{"title":"www.taradigm.com","url":"https://www.taradigm.com/?p=222705"}]

Pricing is inconsistent across sources, and I did not find Oracle's or Autodesk's official Manage price, so verify with a reseller or the vendor before budgeting.

**Primavera P6 Professional:** One third-party guide puts it at $2,570 for an annual subscription, which includes $2,020 plus an annual maintenance fee of $550. A reseller, Taradigm, instead lists a perpetual license at $3520, with optional yearly Oracle support and maintence for an extra $704 per year. A third guide gives a broader range of around $2,500 to $3,500 per user one-time, plus around $500 to $800 per year for optional support.

**Primavera Cloud:** The same guide lists per-user annual rates for its modules: Oracle Primavera scheduling cloud service: $1,320 user/year; Oracle Primavera task management cloud service: $660 user/year; Oracle Primavera progress cloud service: $144 user/year; Oracle Primavera portfolio planning cloud service: $2,640 user/year. I could not confirm these against Oracle's own price list.

**Navisworks Manage:** Autodesk's pages in these results omitted the Manage price in the extracted text. The one Autodesk price I could read is for Simulate, at $1,110/year for 1 user, with a 3-year term at $3,330. A reseller-style aggregator lists Manage at $2,285 billed yearly or $6,170 billed 3 years, though that page's pricing may be stale.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:46:02.321Z

<details><summary>نتيجة أداة (3074 حرف)</summary>

```
Web search results for query: "QGIS licence GPL ArcGIS Pro pricing per year ArcGIS Online named user; Coohom pricing; SketchUp pricing Go Pro Studio"

Links: [{"title":"plans and pricing brl","url":"https://www.sketchup.com/en/plans-and-pricing-brl"},{"title":"plans and pricing brl","url":"https://www.sketchup.com/ja-jp/plans-and-pricing-brl"},{"title":"plans and pricing brl","url":"https://www.sketchup.com/ko-kr/plans-and-pricing-brl"},{"title":"plans and pricing","url":"https://sketchup.trimble.com/pl/plans-and-pricing"},{"title":"plans and pricing brl","url":"https://www.sketchup.com/zh-cn/plans-and-pricing-brl"},{"title":"Plans and Pricing","url":"https://www.sketchup.com/buy/pricing"},{"title":"plans and pricing","url":"https://www.sketchup.com/zh-Hant-TW/plans-and-pricing"},{"title":"plans and pricing","url":"https://sketchup.com/plans-and-pricing?gclsrc=ds"},{"title":"sketchup.com","url":"https://sketchup.com/store"},{"title":"Plans and Pricing","url":"https://www.sketchup.com:443/en/plans-and-pricing"},{"title":"plans and pricing mxn","url":"https://www.sketchup.com/zh-cn/plans-and-pricing-mxn"},{"title":"plans and pricing brl","url":"https://www.sketchup.com/zh-hant-tw/plans-and-pricing-brl"},{"title":"plans and pricing mxn","url":"https://www.sketchup.com/zh-hant-tw/plans-and-pricing-mxn"},{"title":"plans and pricing","url":"https://sketchup.trimble.com/zh-hant-tw/plans-and-pricing"},{"title":"plans and pricing","url":"https://www.sketchup.com/zh-CN/plans-and-pricing"},{"title":"plans and pricing","url":"https://sketchup.com/zh-hant-tw/plans-and-pricing"},{"title":"plans and pricing","url":"https://sketchup.trimble.com/ja/plans-and-pricing"},{"title":"SketchUp Pricing Overview","url":"https://www.g2.com/products/sketchup/pricing"},{"title":"Pricing Update - FAQ","url":"https://prod-aws-help.sketchup.com/pricing-update"}]

I ran one search, and it only covered SketchUp. The QGIS, ArcGIS Pro/Online, and Coohom parts of your query returned nothing, so I haven't verified them. I can search each separately if you want.

**SketchUp (US$, annual, from the results):**
- The official store page lists Go at $119/year, and the Pro and Studio tiers are listed on the same page. A 2024 price-update FAQ gives Go $119/yr, Pro $349/yr, Studio $749/yr, with UK and EU prices in pounds and euros.
- A third-party G2 page, last updated April 2026, lists higher figures: Go $129, Pro $399, Studio $819 per seat per year. Treat that as possibly outdated or region-specific, and check the official page before relying on it.
- Studio is the tier that adds Revit and point-cloud imports. The official page notes Studio (Everything Pro plus), and one regional page describes Studio as Windows only.
- Monthly plans exist for Go and Pro, with annual subscriptions for all offerings.
- Regional pages also show different currencies and prices, and some regional pages mention a 20% discount on annual Pro and Studio plans, which I could not verify.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### user · 2026-11-20T06:46:02.797Z

<details><summary>نتيجة أداة (3867 حرف)</summary>

```
Web search results for query: "Bentley OpenBuildings Designer ProjectWise subscription pricing virtuoso subscription"

Links: [{"title":"www.bentley.com","url":"https://www.bentley.com/en/products/brands/aecosim"},{"title":"openbuildings designer","url":"https://www.bentley.com/products/openbuildings-designer"},{"title":"www.applytosupply.digitalmarketplace.service.gov.uk","url":"https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/722749461633199"},{"title":"www.applytosupply.digitalmarketplace.service.gov.uk","url":"https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/services/722749461633199"},{"title":"www.bentley.com","url":"https://www.bentley.com/software/openbuildings/"},{"title":"www.bentley.com","url":"https://www.bentley.com/en/products/projectwise/"},{"title":"bentley.com","url":"https://bentley.com/projectwise"},{"title":"www.bentley.com","url":"https://www.bentley.com/en/Products/Product-Line/Project-Delivery-Software/ProcureWare"},{"title":"OpenBuildings Designer","url":"https://mcstaging.us.bentley.com/openbuildings-designer"},{"title":"ProjectWise 365","url":"https://www.bentley.com/en/Products/Product-Line/Project-Delivery-Software/ProjectWise-365"},{"title":"www.applytosupply.digitalmarketplace.service.gov.uk","url":"https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/602423733818424"},{"title":"www.bentley.com","url":"https://www.bentley.com/products/projectwise"},{"title":"openbuildings designer","url":"https://www.bentley.com/es/products/openbuildings-designer/"},{"title":"openbuildings designer","url":"https://www.bentley.com/de/products/openbuildings-designer/"},{"title":"www.bentley.com","url":"https://www.bentley.com/en/products/brands/openbuildings"},{"title":"Design Safe, Sustainable, and Distinctive Buildings","url":"https://bentley.com/?p=6472"},{"title":"www.bentley.com","url":"https://www.bentley.com/en/products/brands/projectwise"},{"title":"openbuildings designer","url":"https://www.bentley.com/software/openbuildings-designer/"}]

Bentley's pricing pages show a 12-month Virtuoso subscription as the main entry point for both products, but the ProjectWise figures conflict.

- **OpenBuildings Designer:** Bentley's pages list a starting price of $3,844 USD for the 12-month Virtuoso subscription, and say the price varies by region. The Spanish-language page lists the same $3,844 USD starting price under a 12-month Virtuoso subscription. Speedikon comes bundled with the purchase and is not available for individual purchase.
- **ProjectWise:** One Bentley page lists a starting price of $960.00 USD for a 12-month Virtuoso subscription that includes 1 license. A different Bentley ProjectWise page gives a starting price of $312.00 USD, and the search results don't explain the gap, so I'd treat the $960 figure as unverified. The ProjectWise product page also lists "Contact Us for Pricing" for some options.
- **ProjectWise Bundle (ProjectWise 365):** This bundle starts at $10,440.00 USD for a 12-month Virtuoso subscription that includes 1 license and 15 Connect subscriptions.
- **What the Virtuoso subscription includes:** It bundles a 12-month license for trusted Bentley software with customizable training from experts. The Keys (credits) can be used for training and services; the ProjectWise page mentions 2 Keys per license for training or services.
- **UK government marketplace:** A UK G-Cloud listing for ProjectWise shows £7,287.50 an instance a quarter. That is a different billing structure from the annual US list prices.

Bentley's prices are listed as starting prices, and the search results don't include a full quote for any configuration. Confirm current pricing through Bentley's eStore or a reseller.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

</details>

### assistant · 2026-11-20T06:47:53.366Z

**أداة:** `Write`

```json
{
 "file_path": "/private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/COMPARE_SYSTEMS.md",
 "content": "# T.O X versus the well-known systems (2026-11-20)\n\n## ملخص بالعربي (6 سطور)\n1. T.O X صفحة HTML واحدة مجانية بتشتغل أوفلاين وبتجمع (موديل، رسم، جدول P6، تنسيق، مستندات DC، GIS، وكلاء) في مكان واحد؛ ماحدش من المنافسين بيعمل كده بدون ترخيص وبدون سيرفر.\n2. نقطة قوتها: التكلفة صفر، السرعة في الفتح، وجسر الوكلاء (`window.TOX` + WebSocket)؛ نقطة ضعفها: مفيش سيرفر فالصلاحيات \"تعاونية مش أمنية\"، ومفيش DWG/RVT/NWD حقيقي.\n3. الأنظمة المدفوعة (Revit، ACC، Procore، ProjectWise، Primavera) أقوى في الصلاحيات الحقيقية، التدقيق، التوسع على مشاريع ضخمة، والتوافق مع الصيغ الأصلية.\n4. المفتوحة (Speckle، That Open، Bonsai، FreeCAD، QGIS) أقرب لفلسفة T.O X؛ وأنفع ما يتاخد منها: web-ifc لقراءة IFC و BCF و IDS كلها تشتغل في المتصفح بدون سيرفر.\n5. أعلى 5 تحسينات قيمة/جهد: صلاحيات وموافقة لكل أمر وكيل، وسيط وناتج للأمر، سجل تدقيق دائم، BCF، قراءة IFC بـ web-ifc.\n6. المخاطر الأساسية: حقن أوامر عبر المستندات، سر الجسر في localStorage، ادعاء صلاحيات وهمية، وأسعار الموردين اللي بتتغير؛ كل رقم سعر هنا لازم يتراجع قبل أي قرار.\n\n## How to read this file\n- **[V]** = the claim appeared in a web search result excerpt from the URL cited, 2026-11-20. Excerpts, not always full pages. Prices change by region and date: re-check before any decision.\n- **[V-weak]** = seen only on a third-party aggregator or review site, URL given. Conflicting numbers are shown as conflicting.\n- **[M]** = from my own memory, no URL read in this session. Re-check before relying on it. All strengths, weaknesses and \"what a browser tool can take\" lines are [M] unless a URL is next to them.\n- **[R]** = read directly from T.O X's own docs in this repo (`MEETING_ROOM.md`, `research/*.md`). No source file was read or edited.\n- No vendor code or artwork copied. No value invented: \"unknown\" means unknown.\n\n## 0. What T.O X is today (all [R] from `docs/MEETING_ROOM.md`, `research/AGENT_CONTROL.md`, `research/gap_*.md`)\n- One HTML file (about 1.8 MB), no server. Tabs per discipline: model, drafting, schedule (P6-style CPM, XER and MS Project XML export), survey, coordination (Navisworks-style), detection, take-off, levels, simulation, analysis, office; GIS and environment tab; technical office and document control (22 document types, auto numbers, status, due dates, link to schedule activity); calendar, Telegram bot, handover \"Pulse\" rules; teams, 120-step history in IndexedDB, activity log, live session in the same browser (BroadcastChannel) or WebRTC copy-paste.\n- Exports: IFC2X3 (opened by ifcopenshell in a test: 57 products, 0 failures), DXF (ezdxf, no audit errors), OBJ, XLSX, PDF, SVG, project ZIP. Not tested: opening any export in AutoCAD, Revit, Plant 3D, Navisworks. DWG, RVT, NWD cannot be written by a web page.\n- Roles are \"cooperative, not security\" (the build log says so). No real login or server-side permission.\n- Agents: `window.TOX` (commands, run(id) with no arguments and no result, state, pulse, docs, search) plus an optional WebSocket bridge with a shared secret. Known gaps: no arguments, no structured result, no per-command permission, no approval prompt, audit log only 60 lines in memory, secret in plain localStorage (`AGENT_CONTROL.md` section 1).\n- Calculations are offline code (ASCE 7 wind and seismic, site class, weather scenario). Egyptian code (ECP) methods not done.\n- Clash detection is mesh bounding-box level plus clearances and time-based site conflicts; the Navisworks gap file lists the full clash workflow (tests, rules, statuses) as missing.\n- Live internet features (radio, YouTube, Telegram, Google) were only mock-tested; real-browser behaviour not verified.\n\n---\n\n## 1. System by system\n\nTemplate per system: pricing, openness, 3 strengths, 3 weaknesses, what a browser-only free tool can realistically take, what T.O X can do better.\n\n### 1.1 Autodesk Revit and Autodesk Construction Cloud (ACC, formerly BIM 360)\n- **Pricing:** Revit standard subscription $380/month, $3,005/year, $9,020 for 3 years per Autodesk's FAQ [V: https://www.autodesk.com/solutions/revit-subscription-faq]. Third parties list slightly different numbers [V-weak: https://www.capterra.com/p/265023/Revit/pricing/]. Flex pay-as-you-go tokens exist, $300 per 100 tokens, Revit uses 10 tokens a day [V, same FAQ search]. ACC / Autodesk Build price: not found, contact sales (not verified).\n- **Openness:** proprietary desktop product; open APIs through APS (OAuth with PKCE for single-page apps works from a browser) [V: https://aps.autodesk.com/blog/getting-token-pkce-single-page-app]; Revit MCP server by Autodesk exists per `AGENT_CONTROL.md` (Apache 2.0, Revit 2027) [R, not re-checked]. Design Automation runs headless, billed by usage, 100 calls/min per app [V: https://aps.autodesk.com/en/docs/design-automation/v3/developers_guide/rate-limits/da-rate-limits].\n- **Strengths [M]:** (1) deep parametric families and a huge element library; (2) schedules, sheets and documentation tied to one model; (3) worksharing plus cloud common data environment (ACC) with role-based project access.\n- **Weaknesses [M]:** (1) cost and per-seat licences; (2) heavy install, large models slow on modest PCs; (3) closed file format; automation needs C# add-ins built on a desktop.\n- **A browser tool can take:** the UI frame (Project Browser, Properties palette, Type Selector, View Control Bar, Options Bar, all [V] in `gap_revit.md`), IFC export, schedules as tables over element parameters, optional ACC connector with PKCE (calls only; webhooks need a server [R]).\n- **T.O X can do better:** zero cost; opens in seconds and offline; scripts and agents can drive every command by id; the same page also holds schedule, DC register and handover rules, which Revit alone does not.\n\n### 1.2 Trimble Connect\n- **Pricing:** Personal plan is free: one project, up to five invited members, 10 GB [V: https://community.trimble.com/blogs/lindsay-renkel/2025/05/05/trimble-connect-new-pro-and-innovate-plans-faq via search]. Business Premium $23.95 per user per month billed annually on the official page [V: https://geospatial.trimble.com/en/products/software/trimble-connect/subscription-plans]. Since 20 May 2025 Pro and Innovate plans replace Business and Business Premium for new web purchases (same Trimble post). Older third-party numbers conflict [V-weak: https://www.capterra.co.uk/software/208909/trimble-connect].\n- **Openness:** proprietary cloud; public APIs and openCDE participation [M]; reads IFC [M].\n- **Strengths [M]:** (1) free tier with real project storage; (2) works on web, mobile and field hardware from the same vendor; (3) good IFC and model viewing with issues (BCF-style).\n- **Weaknesses [M]:** (1) free tier limited to one project and five invites [V above]; (2) advanced BIM tools sit in paid plans [V: the Trimble plans page says Business Premium adds them]; (3) needs the cloud and an account.\n- **A browser tool can take:** BCF issues, folder/CDE structure with version history, free-tier-style simple sharing.\n- **T.O X can do better:** no account, no storage cap, no project count limit; project data stays on the user's machine; works with no internet.\n\n### 1.3 Bentley (OpenBuildings Designer, ProjectWise)\n- **Pricing:** OpenBuildings Designer starts at $3,844 for a 12-month Virtuoso subscription [V: https://www.bentley.com/products/openbuildings-designer]. ProjectWise starting price shows $960 on one page and $312 on another (conflict, unexplained) [V: https://www.bentley.com/en/products/projectwise/]; ProjectWise bundle starts at $10,440 with 1 licence plus 15 Connect subscriptions [V: https://www.bentley.com/en/Products/Product-Line/Project-Delivery-Software/ProjectWise-365].\n- **Openness:** proprietary; IFC and open standards support is claimed by Bentley (not checked here) [M].\n- **Strengths [M]:** (1) infrastructure and large-asset strength (roads, rail, plant, utilities); (2) ProjectWise document control with workflows, used by large owners; (3) federated multi-discipline handling at big scale.\n- **Weaknesses [M]:** (1) high price and sales-led purchase; (2) steep learning curve; (3) smaller community and fewer free learning resources than Autodesk.\n- **A browser tool can take:** the ProjectWise ideas of document status workflow, naming rules and transmittals (T.O X already has a DC register).\n- **T.O X can do better:** cost, onboarding time (opens and works), bilingual Arabic/English UI [R], and agents over the same DC register.\n\n### 1.4 Graphisoft Archicad / BIMcloud\n- **Pricing:** two subscription plans now, Archicad Studio (BIMcloud Basic) and Archicad Collaborate (BIMcloud SaaS) [V: https://architosh.com/2025/03/graphisoft-launches-archicad-studio-subscription-plan/]. Prices vary by country and date: Solo €148 or US$200 per month in different pages, Collaborate $406 or $234.17 per month in different pages, BIMcloud $45 or $99 per month (conflicting) [V-weak: https://graphisoft.com/buy-now].\n- **Openness:** proprietary; IFC support and open API/add-on SDK [M].\n- **Strengths [M]:** (1) strong IFC interoperability reputation; (2) fast, light desktop BIM for small and mid practices; (3) BIMcloud delta-based teamwork.\n- **Weaknesses [M]:** (1) smaller market than Revit in many regions; (2) per-seat subscription; (3) automation less common than Revit's add-in ecosystem.\n- **A browser tool can take:** IFC-first workflow and the \"teamwork as deltas\" idea (send changes, not whole files).\n- **T.O X can do better:** price and install; plan, section, sheet, BOQ and schedule in one page.\n\n### 1.5 Procore\n- **Pricing:** annual fee by product, based on annual construction volume; unlimited users, unlimited storage and support included; no public rate card [V: https://procore.com/pricing]. Third-party estimates (USD 15,000 to 80,000 per year for many firms, far higher for large contractors) are unofficial [V-weak: https://www.getonecrew.com/post/procore-pricing].\n- **Openness:** proprietary cloud, public REST API and marketplace [M].\n- **Strengths [M]:** (1) owner, contractor and subcontractor all work in one tenant with project roles; (2) RFIs, submittals, daily logs, punch lists, change events are mature; (3) unlimited users removes per-seat friction [V above].\n- **Weaknesses [M]:** (1) cost scales with construction volume [V above]; (2) not a modelling or CPM scheduling tool; (3) needs internet and sales-led onboarding.\n- **A browser tool can take:** the workflow list (RFI, submittal, NCR, daily log, punch list, change order) and the role matrix per document type. T.O X already has 22 document types [R].\n- **T.O X can do better:** works offline at site, free, and links a document to a schedule activity and a model element in the same page [R]. Cannot match: real multi-party tenant with server enforcement.\n\n### 1.6 Oracle Primavera Cloud and P6\n- **Pricing:** P6 Professional about $2,570/year in one guide, $3,520 perpetual in a reseller page; Primavera Cloud modules priced per user per year (scheduling $1,320 in one guide). Not confirmed on Oracle's own list [V-weak: https://www.projectmanager.com/blog/what-is-primavera-p6, https://www.taradigm.com/?p=222705].\n- **Openness:** proprietary; XER text export is the de facto interchange [M]; Oracle documents the Activities window layouts and Resource Usage Profile [V: https://docs.oracle.com/cd/F74771_01/client_help//en_US/activities_window.htm, https://docs.oracle.com/cd/F74771_01/English/User_Guides/p6_pro_user/the_resource_usage_profile.htm].\n- **Strengths [M]:** (1) accepted standard for large-project CPM and claims; (2) resource and cost loading, baselines, EPS/OBS enterprise structure [V list of concepts in the Activities help]; (3) multi-project portfolio and permissions in the enterprise edition.\n- **Weaknesses [M]:** (1) expensive and dated desktop UI; (2) steep learning curve; (3) slow to do quick what-if work for small teams.\n- **A browser tool can take:** CPM engine (4 relation types, lags, calendars, constraints), top/bottom layout with Activity Details, resource histogram, XER import/export (`gap_p6.md` sections 3-4 [R]).\n- **T.O X can do better:** instant what-if (Monte Carlo risk already built [R]), schedule tied to the 3D model (4D) and to DC documents; free. Missing today per `gap_p6.md`: relationship editing, calendars per activity, baselines, resources.\n\n### 1.7 Microsoft Project\n- **Pricing:** Planner and Project Plan 1 $10, Plan 3 $30, Plan 5 $55 per user per month, annual billing; one source says new Plan 5 purchases ended after 1 May 2026 (single source, unverified) [V: https://www.microsoft.com/en-sg/microsoft-365/project/project-plan-5 and https://thedigitalprojectmanager.com/tools/microsoft-project-pricing].\n- **Openness:** proprietary; MPP file; MS Project XML is a documented interchange [M].\n- **Strengths [M]:** (1) familiar to most office staff; (2) integrates with Microsoft 365 and Teams; (3) resource and cost features at a lower price than P6.\n- **Weaknesses [M]:** (1) per-user cloud subscription; (2) weaker on very large construction logic than P6; (3) tied to the Microsoft ecosystem.\n- **A browser tool can take:** MS Project XML import/export (T.O X exports it already [R]); familiar Gantt conventions.\n- **T.O X can do better:** price, offline, and the schedule can drive a 3D model and a document register.\n\n### 1.8 Autodesk Navisworks\n- **Pricing:** Simulate $1,110/year (3-year $3,330) on Autodesk's page; Manage price not found in Autodesk's text, a reseller-style aggregator shows $2,285 per year [V: https://autodesk.com/products/navisworks/compare; V-weak: https://www.saasworthy.com/product/navisworks/pricing].\n- **Openness:** proprietary NWD/NWF/NWC [M]; reads many formats.\n- **Strengths [M]:** (1) federates many source formats in one review model; (2) Clash Detective with tests, rules, tolerance, statuses (Manage only [V: the dockable windows reference https://help.autodesk.com/cloudhelp/2022/ENU/Navisworks/files/GUID-3539A344-FD91-4F2C-8744-2A5A9828B4C1.htm]); (3) TimeLiner 4D plus quantification.\n- **Weaknesses [M]:** (1) review-oriented, weak authoring; (2) Windows desktop only; (3) cost of Manage and slow with huge models.\n- **A browser tool can take:** Selection Tree and Sets, Find Items, clash tests with statuses, TimeLiner playback, viewpoints. Shortcuts seen in a search snippet: Ctrl+F2 Clash Detective, Ctrl+F3 TimeLiner, Ctrl+F5 Animator, Ctrl+F8 Quantification Workbook, Ctrl+F12 Selection Tree [V-weak: snippet in `gap_navisworks.md`].\n- **T.O X can do better:** model, schedule and review in one page, free, and time-based site clashes (workers, crane swing) already exist [R]. Do not claim NWD compatibility.\n\n### 1.9 Solibri\n- **Pricing:** conflicting. Individual annual $1,200 per user and $149 monthly [V-weak: https://www.trustradius.com/products/solibri-office/pricing]; tier list Starter €99, Essential €1,428, Advanced €2,109, Premium €2,772 per year per licence [V-weak: search snippet, https://store.solibri.com/]. Re-check.\n- **Openness:** proprietary desktop; works through IFC and BCF [V: https://www.trustradius.com/products/solibri-office/pricing says it imports models by IFC].\n- **Strengths [M]:** (1) rule-based model checking (quality, accessibility, code); (2) clear issue reports; (3) vendor-neutral through IFC.\n- **Weaknesses [M]:** (1) review only, no authoring; (2) licence cost; (3) rule sets need expert tuning.\n- **A browser tool can take:** a small IDS-style checker over IFC properties and BCF issue output (IDS is an open buildingSMART standard [V: https://catenda.com/glossary/buildingsmart-standards]).\n- **T.O X can do better:** checks sit beside the model and the register (the Pulse rules already run over documents, activities, risks [R]); free.\n\n### 1.10 BlenderBIM / Bonsai\n- **Pricing:** free.\n- **Openness:** Bonsai GPL-3.0-or-later; IfcOpenShell libraries LGPL [V: https://wiki.osarch.org/index.php/IfcOpenShell and the IfcOpenShell GitHub listing via search].\n- **Strengths [M]:** (1) native IFC authoring; (2) scriptable in Python; (3) free, with an active community.\n- **Weaknesses [M]:** (1) needs Blender and a learning period; (2) BIM UI not familiar to Revit users; (3) heavy for non-technical staff.\n- **A browser tool can take:** nothing inside the page (needs Blender). Reachable as a desktop target through the agent bridge [R, BIM_ECOSYSTEM.md].\n- **T.O X can do better:** no install, familiar ribbon, one file.\n\n### 1.11 FreeCAD\n- **Pricing:** free [M]. Licence LGPL [M, not verified this session]. FreeCAD imports IFC when ifcopenshell is present [V: https://wiki.freecad.org/IfcOpenShell].\n- **Strengths [M]:** (1) parametric solid modelling; (2) Python scripting and headless use; (3) open formats.\n- **Weaknesses [M]:** (1) UI and workflow rough for architects; (2) topological-naming problems in older versions; (3) BIM workbench smaller than commercial BIM.\n- **A browser tool can take:** nothing in-page; a server-side agent target.\n- **T.O X can do better:** instant start, project-level tabs, documents and schedule in the same place.\n\n### 1.12 Speckle\n- **Pricing:** free Explore plan: up to 10 users, 1 project, 30-day history, 100 versions, 50 monthly syncs; paid plans by syncs and versions; self-hosting free [V: https://speckle.systems/pricing/ and https://docs.speckle.systems/workspaces/new-plans-faq]. Pricing changed in 2026 [V: https://osarch.org/2026/01/21/speckle-announces-project-and-usage-based-plans/].\n- **Openness:** server and viewer Apache-2.0 (enterprise modules separate) [V: https://github.com/specklesystems/speckle-server per `BIM_ECOSYSTEM.md`; viewer open source per https://docs.speckle.systems/developers/viewer/].\n- **Strengths [M]:** (1) data-first exchange between Revit, Rhino, Grasshopper, Blender and others; (2) open viewer embeddable in a page; (3) versioned object model with API.\n- **Weaknesses [M]:** (1) free tier tight (1 project) [V above]; (2) depends on connectors installed in desktop tools; (3) hosted model needs internet and account.\n- **A browser tool can take:** an optional \"send/receive\" connector and the idea of versioned object commits. CORS from a static page not tested [R, BIM_ECOSYSTEM.md].\n- **T.O X can do better:** no quota, offline, includes document control and schedule that Speckle does not.\n\n### 1.13 That Open Engine (web-ifc, components)\n- **Pricing:** free.\n- **Openness:** web-ifc MPL-2.0 per most sources, one says MIT, check the repo LICENSE [R, BIM_ECOSYSTEM.md; https://github.com/ThatOpen/engine_web-ifc]. Runs fully in the browser as WebAssembly [R].\n- **Strengths [M]:** (1) the same \"browser only\" philosophy as T.O X; (2) reads and writes IFC in JS; (3) active open community.\n- **Weaknesses [M]:** (1) a toolkit, not a finished product; (2) component API changes quickly; (3) authoring tools are limited.\n- **A browser tool can take:** all of it: IFC import as a locked layer, IFC4X3 option, BCF, fragments for big models.\n- **T.O X can do better:** it is a finished workspace (schedule, DC, coordination) rather than building blocks. Best path is to use web-ifc inside T.O X.\n\n### 1.14 QGIS and ArcGIS\n- **Pricing:** QGIS free, GPL [M, not verified this session]. ArcGIS Pro / Online per named user per year: price not verified this session (search returned nothing) [unknown].\n- **Openness:** QGIS open source with plugins and Python; ArcGIS proprietary with a large API set (ArcPy, JS API) [M].\n- **Strengths [M]:** (1) real GIS analysis, projections and big raster/vector data; (2) huge plugin ecosystems; (3) standard formats (GeoPackage, shapefile, GeoJSON).\n- **Weaknesses [M]:** (1) heavy for a quick site check; (2) steep learning; (3) ArcGIS licensing cost.\n- **A browser tool can take:** MapLibre/Leaflet tiles and GeoJSON import/export, CRS conversion with a small library, KML.\n- **T.O X can do better:** project-centric GIS tab tied to the model (sun path, wind, seismic, offline simulation [R]); it will not match real geoprocessing and should say so.\n\n### 1.15 Coohom\n- **Pricing:** not verified (search returned nothing) [unknown].\n- **Openness:** proprietary cloud interior design service [M].\n- **Strengths [M]:** (1) large furniture and material library; (2) quick room layout and cloud rendering; (3) easy for non-professionals.\n- **Weaknesses [M]:** (1) library and renders tied to the vendor cloud; (2) limited engineering or BIM output; (3) cost of render credits (not verified).\n- **A browser tool can take:** its workflow (room, library, drag, render) with own simple parametric items; `coohom_tab_spec.md` exists [R].\n- **T.O X can do better:** items carry cost, brand and IFC class (hover data [R]) so interior layouts feed BOQ; offline.\n\n### 1.16 SketchUp\n- **Pricing:** Go $119, Pro $349, Studio $749 per year on SketchUp's 2024 price-update FAQ; a review site shows higher numbers [V: https://prod-aws-help.sketchup.com/pricing-update; V-weak: https://www.g2.com/products/sketchup/pricing]. Studio adds Revit and point-cloud import [V-weak, same G2/sketchup pages].\n- **Openness:** proprietary; Ruby extension API and 3D Warehouse [M].\n- **Strengths [M]:** (1) fastest push/pull modelling to learn; (2) huge extension and component library; (3) web version exists.\n- **Weaknesses [M]:** (1) weak BIM data and quantities by default; (2) extensions needed for documentation; (3) subscription.\n- **A browser tool can take:** push/pull, inference-style snapping, groups/components, section planes (`sketchup_tab_spec.md` [R]).\n- **T.O X can do better:** the sketch becomes a priced, scheduled, IFC-classed model in the same page.\n\n### 1.17 AI-first design tools (Arcol, Snaptrude, Hypar, Autodesk Forma, TestFit)\n- **Pricing (all weak):** Forma Building Design free for Revit and AEC Collection subscribers per Autodesk-linked roundups [V-weak: https://resources.rework.com/tools/ai-tools/best-ai-tools-for-architects-2026]; Snaptrude about $499/year and a free option; TestFit reported from $100 to $250 per month (two sources disagree); Hypar free tier, paid on request; Arcol freemium. Treat all as unverified. See also https://architosh.com/2026/01/a-new-center-of-gravity-arcol-is-rebuilding-architectural-authoring/.\n- **Openness:** all proprietary cloud services [M]; Hypar exposes functions and APIs [M].\n- **Strengths [M]:** (1) fast massing, yield and feasibility studies; (2) real-time collaboration (Arcol, Snaptrude); (3) generative or rule-driven layouts (Hypar, TestFit).\n- **Weaknesses [M]:** (1) design-stage only; thin construction documentation; (2) cloud and subscription dependence; (3) model detail and IFC fidelity vary by tool.\n- **A browser tool can take:** a feasibility panel (area, units, parking yield from simple rules), program-to-massing and cost-per-area estimate. All client-side maths.\n- **T.O X can do better:** an agent can run the whole chain from brief to handover gates (the 9-stage lifecycle in `BIM_ECOSYSTEM.md` section D [R]) with human approval gates, and the output feeds BOQ, schedule and DC. Weaker: no generative solver today.\n\n---\n\n## 2. Cross-cutting comparison: what T.O X can do better, and where it cannot\n\n| Topic | Where T.O X is better | Where T.O X is weaker or cannot compete |\n|---|---|---|\n| Permissions and roles (owner, contractor, consultant) | Role views can be built cheaply and shown per document type; per-command agent permission is a small change (section 4, items 1-3). | Today \"cooperative, not security\" [R]. Real enforcement needs a server and identity (ACC, Procore, ProjectWise have it). Do not market roles as secure until then. |\n| Flexibility | One file holds model, CAD, schedule, DC, GIS; any tab can be edited by script. | Not as deep as a dedicated tool in any one domain (families, Civil 3D corridors, P6 enterprise). |\n| Speed | Opens in seconds, no install, no licence check, works offline [R]. | Very large models: performance on big models is listed as to-do [R]. |\n| Keyboard shortcuts | Can copy proven sets cheaply (F9 schedule [V in gap_p6]; Navisworks Ctrl+F keys seen in a snippet) and add a command palette. | No complete verified shortcut table for Revit or AutoCAD was read this session; the CAD command line is still on the to-do list [R]. |\n| Time saved | Fewer round trips: DC register, schedule and model together; agents fill repetitive registers. | Time saved is unmeasured; no benchmark exists. Do not claim numbers. |\n| Project workflow | Nine-stage lifecycle with human gates mapped to ISO 19650-2 (eight stages, stage list [V: https://webstore.ansi.org/preview-pages/ISO/preview_ISO+19650-2-2018.pdf]). | No server CDE; handover between companies is by ZIP or link with state in the `#s=` hash [R]. |\n| Automation by agents | `window.TOX` plus bridge exist; MCP server design is clear [R]. Competitors need add-ins (Revit) or paid APIs (APS Design Automation). | Missing arguments, results, permission classes, approvals, audit [R]. Prompt injection from documents is the main risk. |\n| Offline | Core works offline; autosave and IndexedDB history [R]. | Some widgets need internet (radio, YouTube, Telegram) and were mock-tested only [R]. |\n| Cost | Free. | No vendor support, no certification, no insurance. Stamped design remains with licensed engineers [R]. |\n\n---\n\n## 3. Ranked improvements for T.O X (value over effort, highest first)\n\nEffort scale: S = hours to a day, M = days, L = weeks. Value is my judgement from the gap files, not measured.\n\n1. **Per-command permission class and approval for agents** (read-only, edit, destructive; confirm dialog for risky). Value very high, effort S-M. Closes gaps 3-4 in `AGENT_CONTROL.md` [R].\n2. **`TOX.run(id, args)` returning a structured result or error code.** Without it agents cannot work reliably. S-M.\n3. **Persistent audit log** in IndexedDB with export, replacing the 60 in-memory lines. S.\n4. **Move the bridge secret out of plain localStorage** (session-only or WebCrypto-wrapped) and add rate limit and origin binding. S.\n5. **Role templates (owner, contractor, consultant)** that filter registers, show allowed document actions per type, and label clearly \"not security\". S-M.\n6. **BCF (.bcfzip) import and export** with JSZip, no server (open standard [V: https://github.com/buildingSMART/BCF-API]). M. Gives issue exchange with Solibri, Trimble Connect, Navisworks-class tools [M].\n7. **IFC import with web-ifc** as a locked reference layer. M. Largest interoperability gain; check MPL-2.0 file-level terms [R].\n8. **Sets (selection and search sets) and Select Same / Hide / Require** (P0 in `gap_navisworks.md`). M. Feeds clash, TimeLiner and quantities.\n9. **P6 core: relationship editing, calendars, constraints, Activity Details panel** (P0 in `gap_p6.md`). M-L. Without logic the CPM is not trustworthy.\n10. **Command palette (Ctrl+K) and a user-editable shortcut table**, with a printable cheat sheet. S.\n11. **Clash workflow: tests, rules, tolerance, statuses, grouping** (`gap_navisworks.md`). M-L.\n12. **XER import** (tables such as TASK, TASKPRED, PROJWBS, CALENDAR per `gap_p6.md` [M]) so existing programmes load. M.\n13. **IDS XML export plus a small property checker** from the information-requirements step. M.\n14. **Schedules over element parameters with group, sort, totals, CSV/XLSX round trip** (Revit schedule gap, P3 in `gap_revit.md`). M.\n15. **Real offline install (service worker / PWA) and project save to a folder** with the browser file APIs [M, support varies by browser]; plus a hash of each transmittal package for integrity. M.\n\n---\n\n## 4. Feature matrix\n\nLegend: **yes** / **partial** / **no** / **unknown**. T.O X column is from the build log [R] and gap files; other columns are from memory [M] unless noted, so treat the matrix as a starting hypothesis, not evidence. \"ACC\" = Revit with ACC. Abbreviations: TOX, Rvt, TrC (Trimble Connect), Bnt (Bentley), Arc (Archicad), Prc (Procore), P6 (P6/Primavera Cloud), MSP, Nav, Sol, Bon (Bonsai), FC (FreeCAD), Spk (Speckle), TO (That Open), GIS (QGIS/ArcGIS), Coo, SKP, AI (AI-first tools).\n\n| Feature | TOX | Rvt | TrC | Bnt | Arc | Prc | P6 | MSP | Nav | Sol | Bon | FC | Spk | TO | GIS | Coo | SKP | AI |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n| Runs in browser only | yes | no | partial | no | no | partial | partial | partial | no | no | no | no | partial | yes | partial | yes | partial | yes |\n| Works fully offline | yes | yes | no | yes | yes | no | yes | partial | yes | yes | yes | yes | no | yes | yes | no | yes | no |\n| Free to use | yes | no | partial | no | no | no | no | no | no | no | yes | yes | partial | yes | partial | partial | partial | partial |\n| Parametric BIM authoring | partial | yes | no | yes | yes | no | no | no | no | no | yes | partial | no | partial | no | no | partial | partial |\n| IFC read | no | yes | yes | yes | yes | unknown | no | no | yes | yes | yes | yes | yes | yes | partial | unknown | partial | partial |\n| IFC write | partial (IFC2X3 tested) | yes | unknown | yes | yes | no | no | no | no | no | yes | yes | partial | yes | no | unknown | partial | partial |\n| 2D CAD drafting | partial | partial | no | yes | partial | no | no | no | no | no | partial | yes | no | no | partial | no | partial | no |\n| CPM scheduling | partial | no | no | no | no | partial | yes | yes | no | no | no | no | no | no | no | no | no | no |\n| 4D (model linked to schedule) | yes | no | partial | partial | no | no | partial | no | yes | no | partial | no | partial | partial | no | no | no | no |\n| Clash detection | partial | partial | partial | yes | partial | no | no | no | yes | yes | yes | no | partial | partial | no | no | no | no |\n| Rule-based model checking | partial | no | no | partial | partial | no | no | no | partial | yes | partial | no | partial | partial | no | no | no | partial |\n| BCF issues | no | partial | yes | partial | yes | no | no | no | partial | yes | yes | partial | partial | yes | no | no | no | unknown |\n| Document control register (RFI, submittal, NCR) | yes | partial | partial | yes | no | yes | no | no | no | no | no | no | no | no | no | no | no | no |\n| Real server-side permissions and roles | no | yes | yes | yes | yes | yes | yes | yes | no | no | no | no | yes | no | yes | yes | partial | yes |\n| Audit trail of changes | partial (activity log CSV) | yes | yes | yes | yes | yes | yes | partial | no | no | no | no | yes | no | partial | unknown | no | unknown |\n| Multi-user live editing | partial (same browser or WebRTC) | yes | yes | yes | yes | yes | yes | yes | no | no | no | no | yes | no | yes | yes | partial | yes |\n| Agent / API automation | partial (TOX bridge) | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | unknown | yes | unknown |\n| MCP server available | no (designed, not built) | yes | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown |\n| GIS / site context | partial (offline simulation) | partial | partial | yes | partial | no | no | no | no | no | no | no | no | no | yes | no | partial | partial |\n| Quantities / BOQ | yes | yes | partial | yes | yes | partial | no | no | yes | partial | yes | partial | partial | partial | no | partial | partial | partial |\n| Interior library and render | no | partial | no | partial | partial | no | no | no | no | no | partial | no | no | no | no | yes | yes | partial |\n| Arabic / RTL interface | yes | partial | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | partial | partial | unknown | unknown | partial | unknown | unknown | unknown |\n\nCells cited from a source: Navisworks Clash Detective is Manage only [V: Autodesk dockable-windows reference, see 1.8]; Revit offers PKCE browser access for ACC data through APS [V, see 1.1]; MCP server for Revit: exists per `AGENT_CONTROL.md` [R], MCP for the others was not researched, hence \"unknown\" rather than \"no\". Everything else is [M].\n\n---\n\n## 5. Risks\n\n1. **Fake security.** Roles are cooperative only [R]. If a contractor or consultant is told roles protect data, a confidentiality failure follows. Label it and move real roles to a server before multi-company use.\n2. **Prompt injection through documents.** An agent reading letters, RFIs or imported files may obey text inside them. Mitigation: treat all document text as data, require approval for edit or delete commands (items 1-2 above).\n3. **Bridge secret in plain localStorage.** Readable by any script or extension in the same origin [R].\n4. **Data leakage by publishing.** The page holds client project data and coordinates; the build log says ask before publishing and that the entry gate is only visual [R].\n5. **Compatibility claims.** DWG, RVT, NWD cannot be written; IFC and DXF were checked only with open-source readers, never in the vendor products [R]. Do not claim vendor compatibility.\n6. **Licence traps.** web-ifc MPL-2.0 (file-level copyleft) vs one source saying MIT; IfcOpenShell LGPL and Bonsai GPL are not for bundling in the page; the Autodesk Viewer is proprietary and breaks the \"no vendor code\" rule [R]. Re-check each LICENSE before reuse.\n7. **Price and plan drift.** Every price above conflicts across sources or changes by region. Autodesk, Trimble, Speckle and Microsoft changed plans in 2025-2026 [V]. Re-check before any budget or marketing text.\n8. **Engineering liability.** Outputs are drafts; calculations are not stamped; Egyptian code (ECP) methods are not implemented [R]. Say so in any hand-over.\n9. **Scale and performance.** A single HTML file and bounding-box clashes will not match desktop tools on very large models; not benchmarked [R].\n10. **Browser limits.** Browser storage can be cleared; IndexedDB history can be lost; some features were only mock-tested; phones and Safari not tested [R]. Provide folder or ZIP backup (item 15).\n11. **Scope creep.** The owner's list covers many programmes; imitating each \"exactly\" risks half-built tabs. Gap files already show many commands listed but not built [R]. Prefer depth in P0 items.\n12. **Comparison bias.** This file's strengths and weaknesses are largely [M], and several systems (Coohom, QGIS/ArcGIS pricing, FreeCAD licence) were not verified.\n\n---\n\n## 6. What was NOT verified\n- Official current prices for ACC / Autodesk Build, Navisworks Manage, P6 and Primavera Cloud, Solibri, Coohom, ArcGIS, QGIS-licence page, AI-first tools.\n- Licence of FreeCAD's BIM workbench, QGIS, That Open components (search did not return it).\n- Every strength/weakness line marked [M]; the feature matrix cells except where cited.\n- Keyboard shortcut tables for Revit and AutoCAD; time-saving figures; performance numbers.\n- Full pages: most [V] items come from search excerpts, not from reading the whole page.\n"
}
```

### user · 2026-11-20T06:47:54.787Z

**نتيجة أداة:**
```
File created successfully at: /private/tmp/claude-502/-Users-M7--claude-spares-spare-zoqdHX/d72c5c58-ff10-455f-b893-3cef6d2bb5f1/scratchpad/site/docs/research/COMPARE_SYSTEMS.md (file state is current in your context — no need to Read it back)
```

### assistant · 2026-11-20T06:47:57.715Z

**أداة:** `mcp__ccd_turn__wrap_up`

```json
{
 "recap": "Wrote COMPARE_SYSTEMS.md in the research folder: Arabic summary, 17 system blocks, cross-cutting table, 15 ranked improvements, feature matrix, risks. No source file touched. Strengths, weaknesses and most matrix cells are from memory; several prices were not found."
}
```

### user · 2026-11-20T06:47:57.985Z

**نتيجة أداة:**
```
Nothing is pending, so the app draws no box; the recap is the session's status. Your closing message is your answer to the user: write it now, as the last thing you say this turn.
```

### assistant · 2026-11-20T06:48:06.673Z

I wrote `COMPARE_SYSTEMS.md` at `.../scratchpad/site/docs/research/COMPARE_SYSTEMS.md`. It has the 6-line Arabic summary and 17 system blocks. After those come a T.O X versus the field table, the 15 ranked improvements, the feature matrix and 12 risks.

1. **Sources and labels:** every claim is tagged `[V]` (URL seen in a search excerpt), `[V-weak]` (aggregator only), `[M]` (memory) or `[R]` (read from the T.O X docs). I touched no source file.
2. **Mostly unverified:** all strengths and weaknesses and most feature-matrix cells are `[M]`. I read only search excerpts, never full vendor pages.
3. **Prices:** many conflict across sources (Archicad, Solibri, ProjectWise, TestFit). I found no price for ACC/Autodesk Build, Navisworks Manage (Autodesk's own page), Coohom or ArcGIS, so those are marked unknown. I did not verify the licences of FreeCAD's BIM workbench or QGIS.
4. **Top improvements:** per-command agent permissions with approval, `TOX.run` arguments and structured results, a persistent audit log, BCF import/export, and IFC import with web-ifc.
5. **Main risks:** roles are "cooperative, not security" and must not be sold as secure. Prompt injection through documents, the bridge secret in plain `localStorage`, and unconfirmed vendor-compatibility claims are the others.
