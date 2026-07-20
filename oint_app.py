# -*- coding: utf-8 -*-
"""시판 연고 분류 조회기 — 모바일/웹 (Streamlit).

- 데스크톱(oint.py)과 동일한 데이터/로직을 oint_core.py 에서 공유한다.
- 개인정보·비밀키·외부DB 없음 → Streamlit Community Cloud에 그대로 배포 가능.
- 로컬 실행:  streamlit run oint_web/oint_app.py
"""

from __future__ import annotations

import streamlit as st

import oint_core as core


# ─────────────────────────────────────────────
#  기본 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="시판 연고 분류 조회기", page_icon="🧴",
                   layout="centered")


@st.cache_data(show_spinner=False)
def _load():
    rows, notes = core.load_ointment_data()
    return rows, notes


ROWS, NOTES = _load()

# 표시 상한 (모바일 렌더링 부담 방지)
MAX_SHOW = 80

# 분류 필터: 라벨 → cat_filter 코드
FILTER_OPTIONS = {
    "전체": "",
    "스테로이드(단일)": "S",
    "항생제": "A",
    "항진균제": "B",
    "항바이러스": "C",
    "복합제": "D",
    "면역조절제(TCI)": "E",
    "여드름": "F",
    "건선·각화": "G",
    "기타": "H",
}


# ─────────────────────────────────────────────
#  헬퍼
# ─────────────────────────────────────────────
def _s(v) -> str:
    return core._s(v)


def _grade_of(row: dict):
    """(등급, 종류) 반환. 종류: 'steroid' | 'combo' | None."""
    if row.get("구분") == "스테로이드" and row.get("등급_int") is not None:
        return int(row["등급_int"]), "steroid"
    if row.get("복합스테로이드등급") is not None:
        return int(row["복합스테로이드등급"]), "combo"
    return None, None


def _badge(text: str, color: str) -> str:
    return (
        f"<span style='background:{color};color:#fff;border-radius:6px;"
        f"padding:2px 8px;font-size:0.8rem;white-space:nowrap;'>{text}</span>"
    )


def _row_badges(row: dict) -> str:
    """제품 한 줄용 등급/분류 배지 HTML."""
    parts = []
    g, kind = _grade_of(row)
    if g is not None:
        label, color = core.GRADE_INFO.get(g, ("", core.ACCENT))
        prefix = "스테로이드" if kind == "steroid" else "복합·스테"
        parts.append(_badge(f"{prefix} {g}등급", color))
    code = _s(row.get("분류코드"))
    if row.get("구분") == "일반" and code in core.CATEGORY_INFO:
        lbl, col = core.CATEGORY_INFO[code]
        parts.append(_badge(lbl, col))
    return " ".join(parts)


def _copy_text(row: dict, guide: dict) -> str:
    return (
        f"[{_s(row.get('제품명'))}]\n"
        f"{guide['환자안내문']}\n\n"
        f"바르는 방법: {guide['바르는법']}\n"
        f"사용 기간: {guide['기간']}"
    )


def _render_detail(row: dict):
    code = _s(row.get("분류코드"))
    guide = core.get_patient_guide(code)
    g, kind = _grade_of(row)

    # 등급 배지
    badges = _row_badges(row)
    if badges:
        st.markdown(badges, unsafe_allow_html=True)

    # 제품 정보
    info = {
        "성분(국문)": _s(row.get("성분(국문)")),
        "성분(영문)": _s(row.get("성분(영문)")),
        "함량": _s(row.get("함량")),
        "제형": _s(row.get("제형")),
        "제조사": _s(row.get("제조사")),
        "급여·상한가": f"{_s(row.get('급여'))} · {_s(row.get('상한가'))}원",
        "전문/일반": _s(row.get("전문/일반")),
        "처방 구분": _s(row.get("처방구분")),
    }
    if g is not None:
        lbl = core.GRADE_INFO.get(g, ("", ""))[0]
        info["스테로이드 등급"] = f"{g}등급 · {lbl}"
    if _s(row.get("비고")):
        info["비고"] = _s(row.get("비고"))

    md = "\n".join(f"- **{k}**: {v}" for k, v in info.items() if v)
    st.markdown(md)

    # 1~2등급 경고
    if g in (1, 2):
        st.warning("1~2등급(초강력·강력)은 안면·간찰부·소아 사용을 피하고 "
                   "2~3주 이내 단기 사용. 폐쇄요법·간찰부에서는 실제 효력이 상향됩니다.")

    # 환자 설명
    st.markdown("##### 환자 설명")
    st.info(guide["환자안내문"])
    st.markdown(f"- **바르는 방법**: {guide['바르는법']}\n"
                f"- **사용 기간**: {guide['기간']}")
    if guide.get("주의"):
        st.markdown(f"- **주의사항**: {guide['주의']}")

    # 관련 Q&A
    qnas = core.get_qna_for_category(code)
    if qnas:
        st.markdown("##### 이 약 관련 자주 묻는 질문")
        for qa in qnas:
            st.markdown(f"**Q. {qa['Q']}**\n\n{qa['A']}")

    # 복사용 텍스트
    st.markdown("##### 환자 안내문 복사")
    st.caption("아래 상자 오른쪽 위 아이콘을 눌러 복사하세요.")
    st.code(_copy_text(row, guide), language=None)


# ─────────────────────────────────────────────
#  헤더
# ─────────────────────────────────────────────
st.title("🧴 시판 연고 분류 조회기")
st.caption("피부 외용제(연고·크림·로션 등)를 성분·제품명으로 검색하세요. "
           f"현재 {NOTES[0]}, {NOTES[1]} 수록.")
st.caption(core.PATIENT_GUIDE["메타"]["면책"])


# ─────────────────────────────────────────────
#  검색 / 필터
# ─────────────────────────────────────────────
q = st.text_input("검색어 (성분명·제품명)", placeholder="예: 베타메타손, 겐트리손, 후시딘")
cat_label = st.selectbox("분류 필터", list(FILTER_OPTIONS.keys()), index=0)
cat_filter = FILTER_OPTIONS[cat_label]

res = core.search_ointments(ROWS, q.strip(), cat_filter)

# 검색 요약 (스테로이드 등급 안내)
grades = sorted(
    {int(r["등급_int"]) for r in res if r.get("등급_int") is not None}
    | {int(r["복합스테로이드등급"]) for r in res
       if r.get("복합스테로이드등급") is not None}
)
if q.strip() and grades:
    txt = ", ".join(
        f"{g}등급({core.GRADE_INFO.get(g, ('', ''))[0]})" for g in grades)
    st.success(f"'{q.strip()}' → 스테로이드 {txt}")

st.markdown(f"**검색 결과 {len(res)}건**")
if not res:
    st.info("검색 결과가 없습니다. 성분명(국문/영문)이나 제품명 일부로 검색해 보세요.")
else:
    shown = res[:MAX_SHOW]
    if len(res) > MAX_SHOW:
        st.caption(f"많은 결과 중 상위 {MAX_SHOW}건만 표시합니다. "
                   "검색어로 더 좁혀 보세요.")
    for row in shown:
        with st.expander(_s(row.get("제품명"))):
            _render_detail(row)


# ─────────────────────────────────────────────
#  환자 설명서 (전체 안내)
# ─────────────────────────────────────────────
st.divider()
with st.expander("📖 환자 설명서 (전체 안내)"):
    g = core.PATIENT_GUIDE
    t1, t2, t3, t4, t5 = st.tabs(
        ["기본 사용법", "스테로이드 강도", "종류별 안내", "부작용·주의", "자주 묻는 질문"])

    with t1:
        gu = g["공통_사용법"]
        st.markdown(f"**{gu['제목']}**")
        for i, s in enumerate(gu["단계"], 1):
            st.markdown(f"{i}. {s}")
        st.markdown(gu["FTU"])

    with t2:
        sg = g["스테로이드_강도별"]
        st.markdown(f"**{sg['제목']}**")
        st.markdown(sg["원칙"])
        for r in sg["등급표"]:
            st.markdown(
                f"- **{r['강도']}** — 주로: {r['부위']} / "
                f"피해야 할 곳: {r['피해야할곳']} / 권장 기간: {r['기간']}")
        st.markdown("**공통 주의사항**")
        for c in sg["공통주의"]:
            st.markdown(f"- {c}")

    with t3:
        for code, blk in g["효능군별"].items():
            st.markdown(f"**【{blk['이름']}】 {blk['대표']}**")
            st.markdown(blk["환자안내문"])

    with t4:
        bk = g["부작용"]
        st.markdown("**국소(피부) 부작용**")
        for s in bk["국소"]:
            st.markdown(f"- {s}")
        st.markdown("**전신 부작용 (드묾)**")
        for s in bk["전신_드묾"]:
            st.markdown(f"- {s}")
        st.markdown("**🚨 즉시 진료가 필요한 경우**")
        for s in bk["즉시진료"]:
            st.markdown(f"- {s}")

    with t5:
        st.markdown(f"**{core.PATIENT_QNA['메타']['제목']}**")
        for grp in core.PATIENT_QNA["그룹"]:
            st.markdown(f"**━━ {grp['분류']} ━━**")
            for it in grp["항목"]:
                st.markdown(f"**Q. {it['Q']}**\n\n{it['A']}")
