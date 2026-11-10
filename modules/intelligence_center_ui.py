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

    # Visual identity is scoped to PAGE 17; no specialist page styles are modified.
    st.markdown("""
    <style>
    .tic-shell{background:linear-gradient(135deg,#071321 0%,#0b1c2b 55%,#10283a 100%);
      border:1px solid #1d4055;border-radius:18px;padding:24px 26px;margin:0 0 18px 0;
      box-shadow:0 12px 34px rgba(0,0,0,.18);position:relative;overflow:hidden}
    .tic-shell:after{content:"";position:absolute;width:260px;height:260px;right:-90px;top:-145px;
      border:1px solid rgba(74,207,213,.18);border-radius:50%;box-shadow:0 0 0 28px rgba(74,207,213,.035),0 0 0 58px rgba(74,207,213,.025)}
    .tic-eyebrow{font-size:11px;letter-spacing:2.4px;color:#65d5d2;font-weight:800;text-transform:uppercase}
    .tic-title{font-size:29px;line-height:1.2;font-weight:800;color:#f1f7fb;margin:8px 0 5px}
    .tic-sub{font-size:13px;color:#9bb4c5;margin:0}
    .tic-kpi{background:linear-gradient(145deg,#102638,#0b1b29);border:1px solid #234459;
      border-radius:14px;padding:16px 17px;min-height:112px;position:relative;overflow:hidden}
    .tic-kpi:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:#42c6c9}
    .tic-kpi-label{font-size:11px;letter-spacing:1.1px;text-transform:uppercase;color:#91aebe;font-weight:700}
    .tic-kpi-value{font-size:30px;line-height:1.25;color:#f4f8fb;font-weight:800;margin-top:9px}
    .tic-kpi-foot{font-size:11px;color:#6f91a5;margin-top:3px}
    .tic-section{font-size:17px;font-weight:750;color:#dceaf2;margin:17px 0 8px}
    .tic-chip{display:inline-block;border:1px solid #31566a;border-radius:99px;padding:4px 9px;
      color:#8fd8d7;font-size:10px;letter-spacing:.7px;font-weight:800}
    div[data-testid="stTabs"] button{font-weight:700}
    div[data-testid="stTabs"] button[aria-selected="true"]{color:#53d1d0}
    div[data-testid="stMetric"]{background:#0d2030;border:1px solid #1d3d52;padding:12px;border-radius:12px}
    @media(prefers-reduced-motion:no-preference){.tic-kpi{transition:transform .18s ease,border-color .18s ease}
      .tic-kpi:hover{transform:translateY(-2px);border-color:#4abec4}}
    </style>
    <section class="tic-shell">
      <div class="tic-eyebrow">6868 CAPITAL · INTELLIGENCE OPERATIONS</div>
      <div class="tic-title">Trade Intelligence Center</div>
      <p class="tic-sub">Knowledge · Research · Evidence · Decisions &nbsp; <span class="tic-chip">PAGE 17</span></p>
    </section>
    """, unsafe_allow_html=True)
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
        kpis = [
            ("OPEN WORK", len(tasks.get("open") or []), "Technical Office · read only"),
            ("KNOWLEDGE", academy.get("indexed_records", 0), "Indexed library records"),
            ("LEGACY LESSONS", academy.get("legacy_lessons", 0), "Imported reference material"),
            ("MEETING LOG", mtg.get("entries", 0), "Append-only entries"),
        ]
        cards = st.columns(4)
        for col, (label, value, foot) in zip(cards, kpis):
            with col:
                safe_value = value if value not in (None, "") else "—"
                st.markdown(
                    f'<div class="tic-kpi"><div class="tic-kpi-label">{label}</div>'
                    f'<div class="tic-kpi-value">{safe_value}</div>'
                    f'<div class="tic-kpi-foot">{foot}</div></div>',
                    unsafe_allow_html=True,
                )

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
            st.caption("الأرقام من ملف المعمل المنشور؛ لا تُفسَّر كضمان ربحية.")
        else:
            st.caption("ملخص المعمل غير متاح حاليًا؛ راجع صفحة Lab الأصلية.")
        # Compact visual comparison from published snapshots only.
        if hub:
            trial_data = {
                "Research module": list(hub.keys()),
                "Published trials": [int((item or {}).get("n_trials") or 0) for item in hub.values()],
            }
            st.markdown('<div class="tic-section">Research activity · published snapshots</div>', unsafe_allow_html=True)
            st.bar_chart(trial_data, x="Research module", y="Published trials", horizontal=True)
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
        st.markdown("#### Add a source or research claim")
        st.caption("كل مدخل جديد يبدأ Inbox / Unreviewed؛ الاعتماد التجريبي يظل من Lab فقط.")
        with st.form("tic_knowledge_intake_form", clear_on_submit=True):
            intake_title = st.text_input("Claim / source title")
            intake_summary = st.text_area("Summary of the claim", height=90)
            intake_topic = st.text_input("Topic / concept")
            intake_school = st.text_input("School (optional)")
            intake_claim = st.selectbox("Claim type", ["hypothesis", "interpretation", "fact", "disputed"])
            intake_asset = st.text_input("Asset (optional)")
            intake_tf = st.text_input("Timeframe (optional)")
            intake_url = st.text_input("Source URL (optional)")
            intake_submitted = st.form_submit_button("Save to inbox for review")
        if intake_submitted:
            try:
                if not intake_title.strip() or not intake_summary.strip() or not intake_topic.strip():
                    raise ValueError("Title, summary and topic are required.")
                if intake_url.strip() and not intake_url.strip().startswith(("https://", "http://")):
                    raise ValueError("Source URL must start with http:// or https://.")
                knowledge.upsert_record({
                    "title": intake_title.strip(), "summary": intake_summary.strip(),
                    "topic": intake_topic.strip(), "school": intake_school.strip(),
                    "claim_type": intake_claim, "status": "inbox", "evidence_grade": "unreviewed",
                    "asset": intake_asset.strip(), "timeframe": intake_tf.strip(),
                    "source_url": intake_url.strip(), "language": "en",
                    "provenance": [{"kind": "owner_submitted_source" if intake_url.strip() else "owner_submitted_claim",
                                   "url": intake_url.strip()}] if intake_url.strip() else [{"kind": "owner_submitted_claim"}],
                })
                st.success("Saved to Knowledge Inbox as unreviewed; no empirical validation was granted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save knowledge record: {type(exc).__name__}: {exc}")

        rows = knowledge.search_records(query=q, status="" if status == "All" else status, limit=100)
        if grade != "All":
            rows = [r for r in rows if r.get("evidence_grade") == grade]
        st.caption(f"{len(rows)} record(s) shown · consensus or citations alone are not empirical validation.")
        for item in rows:
            with st.container(border=True):
                st.markdown(f"**{item.get('title', 'Untitled')}**")
                st.caption(f"STATUS · {str(item.get('status', 'unknown')).upper()}    /    EVIDENCE · {str(item.get('evidence_grade', 'unknown')).upper()}")
                st.write(item.get("summary", ""))
                st.caption(
                    f"Topic: {item.get('topic', '—')} | School: {item.get('school') or '—'} | "
                    f"Claim: {item.get('claim_type')} | Asset/TF: {item.get('asset') or '—'} / {item.get('timeframe') or '—'}"
                )
                if isinstance(item.get("source_url"), str) and item["source_url"].startswith(("https://", "http://")):
                    st.markdown(f"[Open source]({item['source_url']})")
                details = item.get("details") or {}
                source_class_labels = {
                    "primary": "Primary · original data/research/document",
                    "secondary": "Secondary · independent analysis/report",
                    "marketing": "Marketing · vendor promotional material",
                    "community": "Community · forum/social content",
                    "internal": "Internal · project notes/logs",
                    "unknown": "Unknown · not yet classified",
                }
                current_class = details.get("source_class", "unknown")
                st.caption(f"Source class: {source_class_labels.get(current_class, 'Unknown')}")
                if details:
                    st.json(details)
                if item.get("status") in {"inbox", "review"}:
                    st.markdown("#### Owner review")
                    st.caption("القبول هنا اعتماد تحريري لإدراج المعرفة بالمكتبة فقط؛ لا يرفع Evidence Grade ولا يمنح صلاحية Empirical Validation.")
                    with st.form(f"tic_review_{item['id']}"):
                        decision = st.selectbox(
                            "Decision",
                            ["accept", "reject", "return_to_review", "archive"],
                            format_func=lambda value: {
                                "accept": "Accept into knowledge library",
                                "reject": "Reject this entry",
                                "return_to_review": "Return for more review",
                                "archive": "Archive",
                            }[value], key=f"tic_review_decision_{item['id']}")
                        source_class = st.selectbox(
                            "Source classification",
                            ["unknown", "primary", "secondary", "marketing", "community", "internal"],
                            index=["unknown", "primary", "secondary", "marketing", "community", "internal"].index(current_class)
                            if current_class in {"unknown", "primary", "secondary", "marketing", "community", "internal"} else 0,
                            format_func=lambda value: source_class_labels[value],
                            key=f"tic_review_source_{item['id']}")
                        reason = st.text_area("Reason for decision (required)", key=f"tic_review_reason_{item['id']}")
                        submitted = st.form_submit_button("Record review decision")
                    if submitted:
                        try:
                            knowledge.review_record(item["id"], decision, reason,
                                                     source_class=source_class, actor="owner")
                            st.success("Review decision appended. Evidence grade was not changed.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Could not record review: {type(exc).__name__}: {exc}")
                history = knowledge.list_review_events(item["id"])
                if history:
                    with st.expander(f"Review history · {len(history)} event(s)"):
                        for event in history:
                            st.write(f"{event['created_at'][:16]} · {event['decision']} · {event['source_class']} · {event['actor']}")
                            st.caption(event["reason"])
        if not rows:
            st.caption("لا توجد سجلات مطابقة. ستظهر هنا المعرفة بعد فهرستها ومراجعتها.")

    with research:
        st.markdown("### Research Hub · published snapshots")
        snap = build_command_snapshot()
        hub = snap.get("research_hub") or {}
        st.caption("قراءة فقط من snapshots التي تنشرها وحدات Research Hub؛ لا يتم تشغيل أو تعديل الوحدات من هنا.")
        # Provenance comes from the documented Research Hub audit, not from the
        # presence of a snapshot alone. Mock-only outputs must never look empirical.
        provenance = {
            "truth": "REAL LAB DATA",
            "plateau": "REAL MARKET DATA · METHOD PROBE",
            "regime": "REAL MARKET DATA · DESCRIPTIVE",
            "trail": "MOCK ONLY · awaiting real signal_log",
            "decay": "MOCK ONLY · awaiting real signal_log",
            "consensus": "REAL LAB DATA · descriptive caveats",
            "funnel": "REAL LAB DATA · Chain-only coverage caveat",
        }
        if not hub:
            st.warning("لا توجد snapshots متاحة حاليًا.")
        for key, item in hub.items():
            source_label = provenance.get(key, "PROVENANCE NOT DOCUMENTED")
            with st.container(border=True):
                st.markdown(f"**{key.upper()}**")
                st.caption(f"{source_label}  ·  {item.get('n_trials', 0)} trials  ·  Last published: {item.get('asof') or '—'}")
                if source_label.startswith("MOCK ONLY"):
                    st.warning("هذه النتائج تجريبية مصطنعة وليست قياسًا على إشارات تداول حقيقية؛ لا تستخدم كدليل أداء.")
                elif source_label == "PROVENANCE NOT DOCUMENTED":
                    st.warning("مصدر هذه اللقطة غير موثق في سجل التدقيق؛ لا تعاملها كدليل تجريبي.")
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
        st.markdown("#### Task handoff · proposal only")
        st.caption("المقترح يُحفظ في سجل الاجتماع بانتظار مراجعة المالك؛ لا يغيّر data/office_tasks.json ولا يعيّن مهمة رسمية تلقائيًا.")
        with st.form("tic_task_proposal_form", clear_on_submit=True):
            proposal_title = st.text_input("Proposed task title", key="tic_proposal_title")
            proposal_detail = st.text_area("Task scope / expected outcome", key="tic_proposal_detail", height=110)
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                proposal_priority = st.selectbox("Priority", ["P1", "P2", "P3"], key="tic_proposal_priority")
            with pc2:
                proposal_area = st.text_input("Area", key="tic_proposal_area")
            with pc3:
                proposal_owner = st.text_input("Suggested owner", key="tic_proposal_owner")
            proposal_next = st.text_input("Next action / acceptance check", key="tic_proposal_next")
            proposal_submitted = st.form_submit_button("Save task proposal for review")
        if proposal_submitted:
            try:
                if not proposal_title.strip() or not proposal_detail.strip():
                    raise ValueError("العنوان ونطاق المهمة مطلوبان.")
                meeting.append_entry(
                    entry_type="recommendation",
                    title=proposal_title,
                    body=proposal_detail,
                    owner=proposal_owner,
                    status="awaiting_owner_review",
                    metadata={
                        "kind": "task_proposal",
                        "priority": proposal_priority,
                        "area": proposal_area.strip(),
                        "suggested_owner": proposal_owner.strip(),
                        "next_action": proposal_next.strip(),
                        "official_board_written": False,
                    },
                )
                st.success("اتحفظ مقترح المهمة في سجل الاجتماع — بانتظار مراجعة المالك.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save task proposal: {type(exc).__name__}: {exc}")

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

        entries = meeting.list_entries(limit=500)
        # Proposal lifecycle is queried independently of the 500-entry history view.
        proposals, reviews = meeting.list_task_proposals()
        pending = [p for p in proposals if p.get("id") not in reviews]
        st.markdown(f"#### Task proposals awaiting review · {len(pending)}")
        if proposals:
            for proposal in proposals:
                meta = proposal.get("metadata") or {}
                review = reviews.get(proposal.get("id"))
                state = review.get("status") if review else "awaiting_owner_review"
                with st.container(border=True):
                    st.markdown(f"**{meta.get('priority', 'P2')} · {proposal.get('title', 'Untitled')}**")
                    st.caption(f"REVIEW STATE · {str(state).replace('_', ' ').upper()}")
                    st.write(proposal.get("body", ""))
                    st.caption(f"Area: {meta.get('area') or '—'} · Suggested owner: {meta.get('suggested_owner') or '—'}")
                    st.caption(f"Next action: {meta.get('next_action') or '—'}")
                    if review:
                        st.caption(f"Review note: {review.get('body', '')}")
                    elif proposal.get("id"):
                        st.caption("Official Technical Office board unchanged; review decision is recorded separately.")
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("Approve for manual board entry", key=f"tic_approve_{proposal['id']}"):
                                meeting.append_entry(
                                    entry_type="decision",
                                    title=f"Task proposal approved: {proposal.get('title', '')}",
                                    body="Approved for manual entry by the owner. This action does not write to data/office_tasks.json.",
                                    status="approved_for_board_entry",
                                    owner=proposal.get("owner", ""),
                                    metadata={"kind": "task_proposal_review", "proposal_id": proposal["id"],
                                              "official_board_written": False},
                                )
                                st.rerun()
                        with b2:
                            if st.button("Decline proposal", key=f"tic_decline_{proposal['id']}"):
                                meeting.append_entry(
                                    entry_type="decision",
                                    title=f"Task proposal declined: {proposal.get('title', '')}",
                                    body="Declined by the owner.",
                                    status="declined",
                                    metadata={"kind": "task_proposal_review", "proposal_id": proposal["id"],
                                              "official_board_written": False},
                                )
                                st.rerun()
        else:
            st.caption("No task proposals yet.")
        st.markdown(f"#### History · {len(entries)} latest entries")
        if not entries:
            st.caption("السجل الجديد فارغ حتى الآن. سجل الاجتماع التاريخي الأصلي محفوظ في docs/MEETING_ROOM.md.")
        for item in entries:
            heading = f"{item.get('created_at', '')[:16].replace('T', ' ')} · {item.get('entry_type')} · {item.get('title')}"
            with st.expander(heading):
                st.write(item.get("body", ""))
                if item.get("owner"):
                    st.caption(f"Owner: {item['owner']}")
                if isinstance(item.get("related_url"), str) and item["related_url"].startswith(("https://", "http://")):
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
