"""نقطة الدخول: streamlit run app.py  (بلا رمز دخول؛ كلمة مرور اختيارية للوحة الباحث فقط)"""
import os

import streamlit as st

st.set_page_config(page_title="مدرّب الريشة الطائرة الذكي", page_icon="🏸", layout="wide")

# نقل الأسرار (إن وُجدت) إلى متغيرات البيئة قبل استيراد الإعدادات
try:
    for _k in ("BAC_RESEARCHER_PASSWORD", "BAC_DEVELOPER"):
        if _k in st.secrets:
            os.environ.setdefault(_k, str(st.secrets[_k]))
except Exception:  # noqa: BLE001  (لا يوجد ملف أسرار)
    pass

from core import config, db  # noqa: E402
from views import group_module, researcher  # noqa: E402
from views.common import header, inject_css  # noqa: E402

inject_css()
db.init_db()

SECTIONS = {"train": "🏋️ التدريب والتحليل", "researcher": "📊 لوحة الباحث"}


def researcher_gate() -> bool:
    pw = config.researcher_password()
    if not pw or st.session_state.get("r_ok"):
        return True
    code = st.text_input("كلمة مرور لوحة الباحث", type="password", key="r_pw")
    if st.button("دخول", key="r_pw_btn"):
        if code == pw:
            st.session_state["r_ok"] = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة.")
    return False


def main() -> None:
    with st.sidebar:
        view = st.radio("القسم", list(SECTIONS), format_func=SECTIONS.get, key="nav")
        st.divider()
        st.caption(os.getenv("BAC_DEVELOPER", config.DEVELOPER))
    header()
    if view == "researcher":
        if researcher_gate():
            researcher.render()
    else:
        group_module.render("exp")


main()
