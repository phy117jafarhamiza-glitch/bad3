"""شاشة البث المباشر: تعمل بالكامل داخل متصفح اللاعب (JavaScript + MediaPipe) بلا WebRTC ولا خادم وسيط.

الكاميرا (حاسوب أو موبايل) تُفتح في المتصفح نفسه، والتحليل يجري على الجهاز، فلا تأخير شبكة في قياس
زمن الاستجابة. يحتاج الأمر اتصال HTTPS (أو localhost) وإنترنت عند أول تحميل لنموذج الوضعية.
النتائج تعود إلى Streamlit كقيمة للمكوّن، وتُحفظ بعد المراجعة كأي جلسة.
"""
from __future__ import annotations

import base64
import os

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from core import reference
from core.config import MOVE_TYPES, POSTURE_REFERENCE
from core.exercises import apply_difficulty

_component = components.declare_component(
    "bac_live", path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_component"))

MOVE_NOTE = {
    "free": "بدون أداة: تنفيذ الحركة بالجسم فقط (اليد فارغة).",
    "racket": "مع مضرب: يمسك اللاعب المضرب وينفّذ الحركة دون ريشة (أداء ظلّي).",
    "racket_shuttle": "مع مضرب وكرة الريشة: يغذّي المدرب الريشة بعد الإشارة وينفّذ اللاعب الضربة فعلياً.",
}

ROW_DEFAULTS = dict(rt=np.nan, valid=0, flag="no_response", onset_frame=-1, contact_frame=-1, elbow=np.nan, shoulder=np.nan,
                    knee=np.nan, trunk=np.nan, reach=np.nan, hit_height=np.nan, speed_peak=np.nan)


def _clean_row(r: dict) -> dict:
    out = dict(ROW_DEFAULTS)
    for k, v in r.items():
        out[k] = np.nan if v is None else v
    return out


def _analysis_from_value(val: dict, pid, ex, phase, unit, difficulty, move_type) -> dict:
    trials = [_clean_row(r) for r in val.get("trials", [])]
    cards = []
    for c in val.get("cards", []):
        img = c.get("img", "")
        if img.startswith("data:image"):
            cards.append((f"المحاولة {c['idx']} – أداؤك (يسار) مقابل الوضع الصحيح (يمين)", base64.b64decode(img.split(",", 1)[1])))
    return dict(pid=pid, ex=ex.code, phase=phase, unit=unit, difficulty=difficulty, fps=None, trials=trials,
                keyframes=cards, source="live", detected=float(val.get("detected", 0.0)), move_type=move_type)


def render_live(group, pid, dominant, ex, phase, unit, difficulty, move_type):
    """يعرض شاشة البث؛ وعند وصول جلسة جديدة تُخزَّن في session_state['analysis'] ويُعاد dict التحليل."""
    import cv2
    st.info(MOVE_NOTE[move_type] + " ضع الجهاز بحيث يظهر اللاعب كاملاً (من الجانب أو الأمام)، وضع الشاشة بحيث يراها وهو يؤدي. "
            "اضغط «تشغيل الكاميرا» داخل الإطار ثم اسمح للمتصفح باستخدامها.")
    st.caption("التحليل يجري على جهازك؛ لا يُرفع فيديو ولا يُحفظ. زمن الاستجابة اللحظي يعتمد على معدل إطارات الكاميرا "
               "(≈ 30 إطاراً/ث ⇒ دقة نحو ± 33 م.ث)، والقياس البحثي الأدق من «تحليل بعد التمرين» بفيديو عالي الإطارات.")
    n_trials = st.number_input("عدد التكرارات", 1, 30, int(ex.reps), key=f"{group}_live_n")
    p = apply_difficulty(ex, difficulty)
    use_arm = bool(ex.use_wrist and move_type != "free")
    ref_kind = reference.kind_for(ex.contact)
    ok, buf = cv2.imencode(".png", reference.draw_reference(ref_kind, 300, 420))
    cfg = dict(
        stim=dict(p["stim"]), n_trials=int(n_trials), dominant=dominant, use_wrist=use_arm, contact=bool(ex.contact),
        rest_s=round(max(1.5, p["rest_rep"] * 0.15 + 0.5), 2),
        posture_ref={k: [lo, hi, label] for k, (lo, hi, label) in POSTURE_REFERENCE.items() if k not in ("reach", "hit_height")})
    val = _component(cfg=cfg, ref_png=base64.b64encode(buf.tobytes()).decode(), dominant=dominant,
                     nonce=f"{ex.code}-{move_type}", key=f"{group}_live_cmp", default=None)
    last_key = f"{group}_live_last"
    if val and val.get("run") != st.session_state.get(last_key) and val.get("trials"):
        st.session_state[last_key] = val["run"]
        a = _analysis_from_value(val, pid, ex, phase, unit, difficulty, move_type)
        st.session_state["analysis"] = a
        return a
    return None
