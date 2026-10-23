"""مكتبة التمرينات وخطة الوحدات الاثنتي عشرة.

مطابقة لمستند «مكتبة تمرينات تطوير الاستجابة الحركية». جميع القيم مقترحة وتُثبَّت
بعد عرضها على الخبراء ونتائج التجربة الاستطلاعية.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Exercise:
    code: str
    level: int
    name: str
    stimulus: str
    response: str
    sets: int = 3
    reps: int = 6
    skills: tuple = ()          # speed / choice / anticipation / accuracy / technique
    stim: dict = field(default_factory=dict)  # إعدادات مولّد المثيرات
    contact: bool = False       # هل يوجد ضرب بالمضرب (قياس الوضع الحركي)؟
    use_wrist: bool = False     # هل تبدأ الاستجابة بحركة الذراع؟


def _s(mode, dmin=1.0, dmax=3.0, **kw):
    d = {"mode": mode, "delay_min": dmin, "delay_max": dmax}
    d.update(kw)
    return d


LIBRARY: list[Exercise] = [
    Exercise("1-1", 1, "انطلاق إلى علامة واحدة", "لون واحد على الشاشة",
             "انطلاق من وضع الاستعداد إلى علامة أمام الشبكة ثم العودة للمركز",
             3, 6, ("speed",), _s("single_color")),
    Exercise("1-2", 1, "خطوة التهيؤ (Split step)", "إشارة صوتية",
             "قفزة قصيرة مع ثبات وضع الاستعداد", 3, 8, ("speed",), _s("sound")),
    Exercise("1-3", 1, "لمس علامة بالمضرب", "إشارة لونية",
             "مد الذراع ولمس علامة أمامية ثم العودة", 3, 6, ("speed", "technique"),
             _s("single_color"), use_wrist=True),
    Exercise("2-1", 2, "انطلاق لأربع زوايا حسب اللون", "4 ألوان، لكل لون زاوية",
             "انطلاق إلى الزاوية المقابلة للون ثم العودة", 3, 8, ("choice",),
             _s("four_colors")),
    Exercise("2-2", 2, "انطلاق حسب السهم", "سهم يمين/يسار/أمام/خلف",
             "انطلاق في اتجاه السهم ثم العودة", 3, 8, ("choice",), _s("arrows")),
    Exercise("2-3", 2, "انطلاق حسب الرقم", "رقم من 1 إلى 6 يمثل منطقة من الملعب",
             "الوصول إلى المنطقة المرقمة", 3, 6, ("choice",), _s("numbers")),
    Exercise("3-1", 3, "قراءة حركة المدرب", "بدء حركة المدرب قبل ضرب الريشة",
             "توقع الاتجاه والتحرك قبل خروج الريشة", 3, 6, ("anticipation",),
             _s("coach_cue", 1.5, 3.5)),
    Exercise("3-2", 3, "مثير خادع", "إشارة تتغير في آخر لحظة",
             "تعديل الاتجاه أثناء الحركة", 3, 6, ("anticipation", "choice"),
             _s("fake_arrow", fake_prob=0.4)),
    Exercise("3-3", 3, "إشارتان متتاليتان", "إشارة تهيؤ ثم إشارة الاتجاه بعد تأخير متغير",
             "تهيؤ ثم انطلاق فور ظهور إشارة الاتجاه", 3, 6, ("anticipation", "speed"),
             _s("delayed_arrow", 1.0, 2.5)),
    Exercise("4-1", 4, "ضربة الشبكة المستقيمة على إشارة", "إشارة ثم ريشة قصيرة مغذّاة من المدرب",
             "انطلاق للشبكة وأداء ضربة شبكة مستقيمة إلى منطقة الهدف", 3, 6,
             ("accuracy", "technique", "speed"), _s("skill_cue", skill="net_straight"),
             contact=True, use_wrist=True),
    Exercise("4-2", 4, "ضربة الشبكة القطرية على إشارة", "إشارة ثم ريشة قصيرة مغذّاة من المدرب",
             "انطلاق للشبكة وأداء ضربة شبكة قطرية إلى المنطقة المقابلة", 3, 6,
             ("accuracy", "technique"), _s("skill_cue", skill="net_cross"),
             contact=True, use_wrist=True),
    Exercise("4-3", 4, "الرفع من الشبكة على إشارة", "إشارة ثم ريشة قصيرة مغذّاة من المدرب",
             "انطلاق للشبكة ورفع الريشة عالياً إلى عمق الملعب", 3, 6,
             ("accuracy", "technique", "choice"), _s("skill_cue", skill="net_lift"),
             contact=True, use_wrist=True),
    Exercise("4-4", 4, "مهارة شبكة متغيرة حسب الإشارة", "إشارة تحدد المهارة (مستقيمة/قطرية/رفع) ومنطقتها",
             "أداء مهارة الشبكة المطلوبة نحو المنطقة المطلوبة", 3, 6,
             ("accuracy", "choice", "technique"), _s("skill_cue", skill="mixed"),
             contact=True, use_wrist=True),
]

_BY_CODE = {e.code: e for e in LIBRARY}

SKILL_LABELS = {
    "speed": "سرعة الاستجابة",
    "choice": "الاختيار بين مثيرات",
    "anticipation": "التوقع",
    "accuracy": "الدقة",
    "technique": "الأداء الفني",
}


def get_exercise(code: str) -> Exercise:
    return _BY_CODE[code]


def exercises_by_level(level: int) -> list[Exercise]:
    return [e for e in LIBRARY if e.level == level]


# (الأسبوع، الوحدة، المستويات، التمرينات، الغرض، نوع الحركة الموصى به)
# 8 أسابيع × 3 وحدات = 24 وحدة، زمن كل وحدة 90 دقيقة (أيام السبت والاثنين والأربعاء).
_U = [
    # الأسبوعان 1–2: استجابة بسيطة ثم بدء الاختيار – حركة بدون أداة ثم مع مضرب
    (1, (1,), ("1-1", "1-2", "1-3"), "تعريف اللاعب بالمثيرات والأداء الأساسي", "free"),
    (1, (1,), ("1-1", "1-2", "1-3"), "ترسيخ الاستجابة البسيطة بمثيرات أسرع", "free"),
    (1, (1,), ("1-1", "1-2", "1-3"), "تثبيت الاستجابة البسيطة وضبط وضع الاستعداد", "free"),
    (2, (1, 2), ("1-1", "1-3", "2-1"), "الانتقال إلى الاختيار بين مثيرين", "free"),
    (2, (1, 2), ("1-2", "2-1", "2-2"), "استجابة اختيارية بأربعة اتجاهات", "racket"),
    (2, (2,), ("2-1", "2-2"), "ترسيخ الاستجابة الاختيارية", "racket"),
    # الأسبوعان 3–4: استجابة اختيارية كاملة ثم التوقع
    (3, (2,), ("2-1", "2-2", "2-3"), "زيادة عدد المثيرات وتقليل زمن العرض", "racket"),
    (3, (2,), ("2-2", "2-3"), "الاستجابة بحسب الرقم والمنطقة", "racket"),
    (3, (2,), ("2-1", "2-2", "2-3"), "تثبيت المستوى الثاني قبل التوقع", "racket"),
    (4, (2, 3), ("2-3", "3-1"), "إدخال قراءة حركة المدرب (التوقع)", "racket"),
    (4, (2, 3), ("2-2", "3-1"), "التوقع مع الاختيار بين الاتجاهات", "racket"),
    (4, (3,), ("3-1", "3-2"), "إدخال المثير الخادع", "racket"),
    # الأسبوعان 5–6: التوقع ثم أول دمج مع ضربات الشبكة
    (5, (3,), ("3-1", "3-2"), "توقع ومثير خادع", "racket"),
    (5, (3,), ("3-2", "3-3"), "استجابة مع تأخير متغير (إشارتان)", "racket"),
    (5, (3, 4), ("3-3", "4-1"), "أول دمج مع ضربة الشبكة المستقيمة", "racket_shuttle"),
    (6, (3, 4), ("3-2", "4-1"), "الخادع مع الضربة المستقيمة", "racket_shuttle"),
    (6, (3, 4), ("3-3", "4-1", "4-2"), "إدخال ضربة الشبكة القطرية", "racket_shuttle"),
    (6, (3, 4), ("3-1", "4-1", "4-2"), "التوقع مع ضربتي الشبكة المستقيمة والقطرية", "racket_shuttle"),
    # الأسبوعان 7–8: دمج مهارات الشبكة الثلاث ثم المهارة المتغيرة
    (7, (3, 4), ("3-3", "4-2", "4-3"), "إدخال الرفع من الشبكة", "racket_shuttle"),
    (7, (3, 4), ("3-2", "4-1", "4-3"), "الخادع مع المستقيمة والرفع", "racket_shuttle"),
    (7, (3, 4), ("3-3", "4-1", "4-2", "4-3"), "تثبيت دمج مهارات الشبكة الثلاث", "racket_shuttle"),
    (8, (3, 4), ("3-2", "3-3", "4-4"), "مهارة شبكة متغيرة عند أقصى صعوبة", "racket_shuttle"),
    (8, (4,), ("4-1", "4-2", "4-3", "4-4"), "مراجعة شاملة لمهارات الشبكة", "racket_shuttle"),
    (8, (3, 4), ("3-1", "4-4"), "تثبيت ومراجعة قبل الاختبار البعدي (يُفضَّل قبله بـ 48 ساعة)", "racket_shuttle"),
]
UNIT_PLAN: list[dict] = [dict(week=w, unit=i + 1, levels=lv, codes=c, goal=g, move=m, session_in_week=(i % 3) + 1)
                         for i, (w, lv, c, g, m) in enumerate(_U)]

N_UNITS = len(UNIT_PLAN)
UNITS_PER_WEEK = 3
UNIT_MINUTES = 90
WEEK_DAYS = ("السبت", "الاثنين", "الأربعاء")

def move_for(unit: int, ex: "Exercise") -> str:
    """نوع الحركة الموصى به للتمرين في الوحدة (ضربات الشبكة تحتاج مضرباً على الأقل)."""
    m = plan_for_unit(unit)["move"]
    return m if m in allowed_moves(ex) else allowed_moves(ex)[0]


def plan_for_unit(unit: int) -> dict:
    for p in UNIT_PLAN:
        if p["unit"] == unit:
            return p
    raise KeyError(unit)


def exercises_for_unit(unit: int) -> list[Exercise]:
    return [get_exercise(c) for c in plan_for_unit(unit)["codes"]]


# ------------------------------------------------------------ مستوى الصعوبة 1..5
DIFFICULTY_MIN, DIFFICULTY_MAX, DIFFICULTY_DEFAULT = 1, 5, 3


def apply_difficulty(ex: Exercise, difficulty: int) -> dict:
    """يعيد معاملات التنفيذ بعد ضبط الصعوبة (تُستخدم في مجموعة الشبكات العصبية العميقة)."""
    d = max(DIFFICULTY_MIN, min(DIFFICULTY_MAX, int(difficulty)))
    shift = d - DIFFICULTY_DEFAULT
    stim = dict(ex.stim)
    stim["delay_max"] = round(max(stim["delay_min"] + 0.5, stim["delay_max"] - 0.25 * shift), 2)
    if "fake_prob" in stim:
        stim["fake_prob"] = round(min(0.7, max(0.2, stim["fake_prob"] + 0.1 * shift)), 2)
    reps = int(max(4, min(10, ex.reps + shift)))
    rest_rep = 20 - 2 * shift            # ثانية بين التكرارات
    rest_set = 90 - 10 * shift           # ثانية بين المجموعات
    return dict(code=ex.code, name=ex.name, sets=ex.sets, reps=reps,
                rest_rep=rest_rep, rest_set=rest_set, stim=stim, difficulty=d)


def default_prescription(unit: int) -> list[dict]:
    """البرنامج الثابت (مجموعة الرؤية الحاسوبية): نفس الجدول لكل اللاعبين."""
    return [apply_difficulty(e, DIFFICULTY_DEFAULT) for e in exercises_for_unit(unit)]


def allowed_moves(ex: "Exercise") -> tuple:
    """أنواع الحركة الممكنة للتمرين: ضربات الشبكة (المستوى 4) تحتاج مضرباً على الأقل."""
    return ("racket", "racket_shuttle") if ex.level == 4 else ("free", "racket", "racket_shuttle")


# ------------------------------------------------- تقسيم زمن الوحدة (90 دقيقة)
PREP_GENERAL, PREP_SPECIAL = 10, 10          # الإعداد: 20
MAIN_MINUTES = 60                            # الرئيسي: 60
CLOSE_COOL, CLOSE_TALK = 5, 5                # الختامي: 10
REP_CYCLE_S = 10                             # انتظار + استجابة + عودة، لكل تكرار (تقدير)


def unit_schedule(unit: int, difficulty: int = DIFFICULTY_DEFAULT) -> list[dict]:
    """جدول الوحدة بالدقائق: إعداد 20 + رئيسي 60 + ختامي 10 = 90. يُعاد صفوف (القسم، النشاط، الدقائق، التفاصيل)."""
    exs = exercises_for_unit(unit)
    feedback_min = 10
    blocks_total = MAIN_MINUTES - feedback_min - 5                  # 45 دقيقة للتمرينات (5 دقائق للانتقالات)
    n = len(exs)
    mins = [blocks_total // n] * n
    for i in range(blocks_total - sum(mins)):                       # توزيع الباقي بالتساوي
        mins[i % n] += 1
    rows = [
        dict(part="الإعدادي", activity="إحماء عام", minutes=PREP_GENERAL,
             detail="جري خفيف، تمارين حركية ديناميكية للمفاصل، ألعاب صغيرة"),
        dict(part="الإعدادي", activity="إحماء خاص", minutes=PREP_SPECIAL,
             detail="خطوات الريشة (جانبي/أمامي/خلفي)، خطوة التهيؤ Split step، تحريك المضرب أو الحركة الظلية حسب نوع الحركة"),
    ]
    for e, m in zip(exs, mins):
        p = apply_difficulty(e, difficulty)
        set_s = p["reps"] * (REP_CYCLE_S + p["rest_rep"]) + p["rest_set"]
        sets = max(1, round(m * 60 / set_s))
        rows.append(dict(part="الرئيسي", activity=f"{e.code} – {e.name}", minutes=m,
                         detail=f"{sets} مجموعات × {p['reps']} تكراراً؛ راحة {p['rest_rep']} ث بين التكرارات و{p['rest_set']} ث بين المجموعات؛ "
                                f"المثير: {e.stimulus}"))
    rows.append(dict(part="الرئيسي", activity="انتقالات وتهيئة الأدوات", minutes=5,
                     detail="تبديل المثيرات والمناطق وتجهيز الكاميرا والشاشة"))
    rows.append(dict(part="الرئيسي", activity="مراجعة الأداء والتغذية الراجعة", minutes=feedback_min,
                     detail="عرض نتائج المجموعة (زمن الاستجابة والزوايا مقابل الوضع الصحيح) وتحديد نقطة التصحيح للوحدة التالية"))
    rows.append(dict(part="الختامي", activity="تهدئة وإطالة", minutes=CLOSE_COOL, detail="جري خفيف ثم إطالة ثابتة للأطراف السفلية والكتف"))
    rows.append(dict(part="الختامي", activity="تقويم الوحدة", minutes=CLOSE_TALK,
                     detail="مناقشة قصيرة مع اللاعبين وتسجيل ملاحظات الباحث"))
    assert sum(r["minutes"] for r in rows) == UNIT_MINUTES, rows
    return rows
