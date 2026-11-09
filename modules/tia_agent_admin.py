"""Streamlit controls for persistent TIA agent profiles and task inbox."""
from __future__ import annotations

import streamlit as st

from modules.tia_agent_store import TIAStore


def _store():
    if "_tia_agent_store" not in st.session_state:
        st.session_state["_tia_agent_store"] = TIAStore()
    return st.session_state["_tia_agent_store"]


def render_agent_admin():
    st.markdown("### Agent Control · Persistent Team")
    st.caption("الأسماء والتعليمات والمهام تُحفظ في قاعدة بيانات TIA المحلية. هذه واجهة إدارة وسجل مهام؛ لا يوجد عامل خلفية ينفذ المهام بعد.")
    try:
        store = _store()
        agents = store.list_agents()
    except Exception as exc:
        st.error(f"تعذر فتح مخزن TIA: {type(exc).__name__}: {str(exc)[:180]}")
        return

    by_id = {a["agent_id"]: a for a in agents}
    with st.expander("إدارة الأعضاء والأسماء والتعليمات", expanded=False):
        selected_id = st.selectbox(
            "اختر العضو", list(by_id),
            format_func=lambda key: f'{by_id[key]["display_name"]} · {key}',
            key="tia_admin_agent_id",
        )
        agent = by_id[selected_id]
        st.write(agent["profile"].get("mission", ""))
        c1, c2 = st.columns([3, 1])
        new_name = c1.text_input("الاسم الظاهر", value=agent["display_name"], max_chars=80, key=f"tia_name_{selected_id}")
        enabled = c2.toggle("مفعّل", value=agent["enabled"], key=f"tia_enabled_{selected_id}")
        current = store.get_instructions(selected_id)
        do_text = st.text_area("توجيهات يجب أن ينفذها (كل توجيه في سطر)", value="\n".join(current["do"]), height=100, key=f"tia_do_{selected_id}")
        dont_text = st.text_area("ممنوعات وأخطاء لا يكررها (كل قاعدة في سطر)", value="\n".join(current["dont"]), height=100, key=f"tia_dont_{selected_id}")
        if st.button("حفظ إعدادات العضو", type="primary", key=f"tia_save_profile_{selected_id}"):
            try:
                if new_name.strip() != agent["display_name"]:
                    store.rename_agent(selected_id, new_name)
                if enabled != agent["enabled"]:
                    store.set_agent_enabled(selected_id, enabled)
                do_items = [x.strip() for x in do_text.splitlines() if x.strip()]
                dont_items = [x.strip() for x in dont_text.splitlines() if x.strip()]
                if do_items != current["do"] or dont_items != current["dont"]:
                    version = store.set_instructions(selected_id, do_items, dont_items)
                    st.success(f"تم حفظ التعليمات بإصدار {version}.")
                else:
                    st.success("تم حفظ بيانات العضو.")
                st.rerun()
            except Exception as exc:
                st.error(f"لم يتم الحفظ: {type(exc).__name__}: {str(exc)[:180]}")
        st.caption("المعرف الداخلي ثابت؛ تغيير الاسم لا يغيّر سجل العضو. لا تضع مفاتيح API أو كلمات مرور هنا.")

    with st.expander("إسناد مهمة وحفظها في قائمة الفريق", expanded=False):
        active = [a for a in agents if a["enabled"]]
        if not active:
            st.warning("لا يوجد أعضاء مفعّلون.")
        else:
            owner = st.selectbox("المسؤول عن المهمة", [a["agent_id"] for a in active],
                                 format_func=lambda key: f'{by_id[key]["display_name"]} · {key}',
                                 key="tia_task_owner")
            title = st.text_input("عنوان المهمة", max_chars=160, key="tia_task_title")
            description = st.text_area("التوجيه والتفاصيل", height=100, key="tia_task_description")
            kind = st.selectbox("نوع المهمة", ["analysis", "research", "monitoring", "review", "report", "development"],
                                format_func=lambda x: {"analysis":"تحليل","research":"بحث","monitoring":"متابعة","review":"مراجعة","report":"تقرير","development":"تطوير"}[x],
                                key="tia_task_kind")
            ongoing = st.checkbox("مهمة مستمرة (تحتاج تاريخ انتهاء/إيقاف في مرحلة الجدولة)", key="tia_task_ongoing")
            if st.button("حفظ المهمة", key="tia_task_create"):
                try:
                    if not title.strip():
                        st.warning("اكتب عنوان المهمة أولاً.")
                    else:
                        task_id = store.create_task(title, description, owner, task_type=kind,
                                                    ongoing=ongoing, actor="owner")
                        st.success(f"تم تسجيل المهمة: {task_id[:8]}")
                        st.rerun()
                except Exception as exc:
                    st.error(f"تعذر تسجيل المهمة: {type(exc).__name__}: {str(exc)[:180]}")
        st.caption("حفظ المهمة لا يعني بدء تنفيذها؛ لا يوجد worker أو جدولة متصلة حتى الآن.")

    st.markdown("#### قائمة المهام المحفوظة")
    try:
        tasks = store.list_tasks(limit=50)
        if tasks:
            for task in tasks:
                label = f'{task["status"].upper()} · {task["title"]} · {by_id.get(task["owner_agent_id"], {}).get("display_name", task["owner_agent_id"])}'
                with st.expander(label):
                    st.write(task["description"] or "بدون تفاصيل إضافية")
                    st.caption(f'ID: {task["task_id"]} · النوع: {task["task_type"]} · أُنشئت: {task["created_at"]}')
                    history = store.task_history(task["task_id"])
                    if history:
                        st.json([{ "event": e["event_type"], "from": e["from_state"], "to": e["to_state"], "at": e["created_at"], "payload": e["payload"] } for e in history])
                    if task["status"] in ("queued", "blocked"):
                        a, b = st.columns(2)
                        if a.button("بدء المهمة يدوياً", key=f'tia_task_start_{task["task_id"]}'):
                            st.warning("لا يمكن بدء التنفيذ: لا يوجد worker متصل. حالة المهمة تظل كما هي.")
                        if b.button("إلغاء المهمة", key=f'tia_task_cancel_{task["task_id"]}'):
                            store.transition_task(task["task_id"], "cancelled", actor="owner", payload={"reason":"owner_cancelled"})
                            st.rerun()
        else:
            st.info("لا توجد مهام محفوظة بعد.")
    except Exception as exc:
        st.error(f"تعذر قراءة المهام: {type(exc).__name__}: {str(exc)[:180]}")
