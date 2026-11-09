"""Streamlit UI for the Trade Intelligence Center.

This is an additive landing page. Specialist pages remain untouched and available
until the owner approves a tested navigation migration.
"""
from __future__ import annotations

import streamlit as st
from pathlib import Path


def _metric(label: str, value) -> None:
    st.metric(label, value if value not in (None, "") else "—")


def render() -> None:
    from modules.intelligence_center import build_command_snapshot
    from modules import academy_intelligence as knowledge
    from modules import intelligence_meeting as meeting

    st.markdown("## ◈ Trade Intelligence Center")
    st.caption("6868 Capital · Trade Intelligence Agency | مركز المعرفة والبحث وقرارات المشروع")
    st.info(
        "المركز يجمع المعرفة المنشورة، ملخصات البحث، حالة المعمل وسجل الاجتماعات. "
        "لا يغيّر محركات Radar أو Spot أو Technical Office، ولا يحل محل Lab في اعتماد الأدلة."
    )

    overview, library, research, room = st.tabs(
        ["Command Center", "Knowledge", "Research", "Meeting Room"]
    )

    with overview:
        snap = build_command_snapshot()
        tasks = snap.get("tasks") or {}
        academy = snap.get("academy") or {}
        lab = snap.get("lab") or {}
        hub = snap.get("research_hub") or {}
        mtg = snap.get("meeting_room") or {}
        c = st.columns(4)
        with c[0]:
            _metric("Open project tasks", len(tasks.get("open") or []))
        with c[1]:
            _metric("Knowledge records", academy.get("indexed_records", 0))
        with c[2]:
            _metric("Legacy lessons", academy.get("legacy_lessons", 0))
        with c[3]:
            _metric("Meeting entries", mtg.get("entries", 0))

        st.markdown("### Project direction")
        st.write(
            "- Trade Intelligence Center: command overview, shared knowledge, research snapshots and Meeting Room.\n"
            "- Lab remains the only empirical validation authority.\n"
            "- Playbook remains the operational strategy reference.\n"
            "- Technical Office, Radar and Spot remain independent; this page only reads their status or links."
        )
        st.markdown("### Current work queue")
        open_tasks = tasks.get("open") or []
        if open_tasks:
            for task in open_tasks:
                title = task.get("title") or task.get("title_ar") or task.get("wbs") or "Untitled task"
                status = task.get("status", "open")
                st.markdown(f"- **{title}** · {status}")
                if task.get("next") or task.get("next_ar"):
                    st.caption(task.get("next") or task.get("next_ar"))
        else:
            st.caption("لا توجد مهام مفتوحة ظاهرة من لوحة Technical Office، أو تعذر قراءة مصدرها.")
        if lab:
            st.markdown("### Lab evidence snapshot")
            cols = st.columns(4)
            for col, key, label in zip(cols, ("built", "passed", "candidates", "symbols"),
                                       ("Last built", "Passed gate", "Candidates", "Symbols")):
                with col:
                    _metric(label, lab.get(key))
            st.caption("الأرقام من ملف المعمل المنشور؛ لا تُفسَّر كضمان ربحية.")
        else:
            st.caption("ملخص المعمل غير متاح حاليًا؛ راجع صفحة Lab الأصلية.")
        st.markdown("### Connected research snapshots")
        if hub:
            for key, item in hub.items():
                st.write(f"**{key}** · trials: {item.get('n_trials', 0)} · as of: {item.get('asof') or '—'}")
                for finding in item.get("findings") or []:
                    st.caption(str(finding)[:500])
        else:
            st.caption("لا توجد لقطات بحث منشورة أو لم تُقرأ بعد.")
        st.caption(f"Snapshot generated: {snap.get('generated_at', '—')}")

    with library:
        st.markdown("### Shared knowledge")
        knowledge.initialize()
        q = st.text_input("Search title, summary or details", key="tic_knowledge_query")
        f1, f2 = st.columns(2)
        with f1:
            status = st.selectbox("Status", ["All", "inbox", "review", "accepted", "rejected", "archived"],
                                  key="tic_knowledge_status")
        with f2:
            grade = st.selectbox("Evidence grade", ["All", "unreviewed", "source_only", "corroborated",
                                                    "backtest_candidate", "validated"],
                                 key="tic_knowledge_grade")
        rows = knowledge.search_records(query=q, status="" if status == "All" else status, limit=100)
        if grade != "All":
            rows = [r for r in rows if r.get("evidence_grade") == grade]
        st.caption(f"{len(rows)} record(s) shown · consensus or citations alone are not empirical validation.")
        for item in rows:
            with st.expander(f"{item.get('title', 'Untitled')} · {item.get('status')} · {item.get('evidence_grade')}"):
                st.write(item.get("summary", ""))
                st.caption(
                    f"Topic: {item.get('topic', '—')} | School: {item.get('school') or '—'} | "
                    f"Claim: {item.get('claim_type')} | Asset/TF: {item.get('asset') or '—'} / {item.get('timeframe') or '—'}"
                )
                if item.get("source_url", "").startswith(("https://", "http://")):
                    st.markdown(f"[Open source]({item['source_url']})")
                details = item.get("details") or {}
                if details:
                    st.json(details)
        if not rows:
            st.caption("لا توجد سجلات مطابقة. ستظهر هنا المعرفة بعد فهرستها ومراجعتها.")

    with research:
        st.markdown("### Research Hub · published snapshots")
        snap = build_command_snapshot()
        hub = snap.get("research_hub") or {}
        st.caption("قراءة فقط من snapshots التي تنشرها وحدات Research Hub؛ لا يتم تشغيل أو تعديل الوحدات من هنا.")
        if not hub:
            st.warning("لا توجد snapshots متاحة حاليًا.")
        for key, item in hub.items():
            with st.expander(f"{key} · {item.get('n_trials', 0)} trials"):
                st.write(f"Last published: {item.get('asof') or '—'}")
                findings = item.get("findings") or []
                if findings:
                    for finding in findings:
                        st.write(finding)
                else:
                    st.caption("No findings in this published snapshot.")
        st.markdown("### Specialist destinations")
        st.write("- Lab: validation, calibration and evidence authority.")
        st.write("- Playbook: accepted operating rules and execution guidance.")
        st.write("- Radar / Technical Office / Spot: remain in their existing pages and retain their own controls.")

    with room:
        st.markdown("### Meeting Room")
        st.caption("سجل تراكمي: طلبات المالك، القرارات، ما اكتمل، الخطوات التالية، العوائق وتقارير الوكلاء.")
        with st.form("tic_meeting_entry_form", clear_on_submit=True):
            entry_type = st.selectbox(
                "Entry type",
                ["owner_request", "decision", "completed", "next_step", "blocker",
                 "recommendation", "meeting_note", "agent_report", "test_result"],
            )
            title = st.text_input("Title")
            body = st.text_area("Details", height=140)
            owner = st.text_input("Owner / assignee (optional)")
            related_url = st.text_input("Related URL (optional)")
            submitted = st.form_submit_button("Add to Meeting Room")
        if submitted:
            try:
                meeting.append_entry(entry_type=entry_type, title=title, body=body,
                                     owner=owner, related_url=related_url)
                st.success("تمت إضافة المدخلة إلى سجل الاجتماع.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save entry: {type(exc).__name__}: {exc}")

        entries = meeting.list_entries(limit=200)
        st.markdown(f"#### History · {len(entries)} latest entries")
        if not entries:
            st.caption("السجل الجديد فارغ حتى الآن. سجل الاجتماع التاريخي الأصلي محفوظ في docs/MEETING_ROOM.md.")
        for item in entries:
            heading = f"{item.get('created_at', '')[:16].replace('T', ' ')} · {item.get('entry_type')} · {item.get('title')}"
            with st.expander(heading):
                st.write(item.get("body", ""))
                if item.get("owner"):
                    st.caption(f"Owner: {item['owner']}")
                if item.get("related_url", "").startswith(("https://", "http://")):
                    st.markdown(f"[Related link]({item['related_url']})")
                st.caption(f"Actor: {item.get('actor', 'owner')} · Status: {item.get('status', 'recorded')}")

        st.divider()
        st.markdown("### Existing project records")
        st.caption("المحاضر الأصلية محفوظة كما هي؛ العرض هنا للرجوع فقط، ولا يستبدل المحادثات أو المرفقات الأصلية.")
        project_root = Path(__file__).resolve().parent.parent
        for label, relpath in (
            ("Historical Meeting Room · full existing log", "docs/MEETING_ROOM.md"),
            ("Current project Whiteboard", "docs/WHITEBOARD.md"),
            ("Trade Intelligence Center workstream log", "docs/INTELLIGENCE_MEETING_LOG.md"),
            ("Center architecture and migration contract", "docs/INTELLIGENCE_COMMAND_CENTER.md"),
        ):
            with st.expander(label, expanded=False):
                try:
                    content = (project_root / relpath).read_text(encoding="utf-8")
                    st.markdown(content)
                except OSError:
                    st.warning(f"Could not read {relpath} from this build.")
