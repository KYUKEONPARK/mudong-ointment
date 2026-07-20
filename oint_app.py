# -*- coding: utf-8 -*-
"""시판 연고 분류 조회기 — 모바일/웹 (Streamlit).

- 데스크톱(oint.py)과 동일한 데이터/로직을 oint_core.py 에서 공유한다.
- 개인정보·비밀키·외부DB 없음 → Streamlit Community Cloud에 그대로 배포 가능.
- 로컬 실행:  streamlit run oint_web/oint_app.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

import oint_core as core
import ocr


# ─────────────────────────────────────────────
#  기본 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="SR oint · 시판 연고 조회기", page_icon="🦉",
                   layout="centered")

ASSETS = Path(__file__).parent / "assets"
ACCENT_GREEN = "#4CC98A"


@st.cache_data(show_spinner=False)
def _logo_data_uri() -> str:
    """로고 PNG를 base64 data URI로 반환. 없으면 빈 문자열."""
    p = ASSETS / "logo.png"
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


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
#  스타일 (브랜딩)
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <style>
      /* 상단 툴바(Fork/GitHub/메뉴)·하단 배지 숨기기 */
      header[data-testid="stHeader"] {{ display:none; }}
      [data-testid="stToolbar"] {{ display:none !important; }}
      [data-testid="stDecoration"] {{ display:none !important; }}
      [data-testid="stStatusWidget"] {{ display:none !important; visibility:hidden !important; }}
      #MainMenu {{ visibility:hidden; }}
      footer {{ visibility:hidden; }}
      [class*="viewerBadge"], .viewerBadge_container__1QSob,
      .viewerBadge_link__1S137, .stAppDeployButton {{
          display:none !important; visibility:hidden !important;
      }}

      /* 좌우 스와이프 시 화면 밀림 방지(세로 스크롤은 유지) */
      html, body, .stApp {{ overflow-x:hidden !important; max-width:100%; }}
      body {{ overscroll-behavior-x:none; }}

      .stApp {{ background:#f6f9f6; }}
      .block-container {{ padding-top:1.4rem; }}
      /* 브랜드 타이틀 */
      .sr-brand {{ text-align:center; font-weight:800; letter-spacing:1px;
                   line-height:1.1; margin:0.2rem 0 0.4rem; }}
      .sr-brand .sr {{ color:{ACCENT_GREEN}; }}
      .sr-brand .oint {{ color:#1f2933; }}
      .sr-logo {{ display:block; margin:0.2rem auto 0.6rem; }}
      .sr-tagline {{ text-align:center; color:#7b8a83; margin-bottom:0.8rem; }}
      /* 검색창을 둥근 알약 모양으로 */
      div[data-testid="stTextInput"] input {{
          border-radius:26px; border:2px solid #a9dcc4;
          padding:12px 16px; font-size:1.05rem; background:#ffffff;
      }}
      div[data-testid="stTextInput"] input:focus {{
          border-color:{ACCENT_GREEN};
          box-shadow:0 0 0 2px rgba(76,201,138,0.2);
      }}
      /* 검색줄: 모바일에서도 가로 배치 유지(세로로 쌓이지 않게) */
      div[data-testid="stHorizontalBlock"] {{
          flex-wrap:nowrap; align-items:center; gap:0.4rem;
      }}
      /* 컬럼이 화면 밖으로 넘치지 않게 축소 허용(왼쪽 밀림 방지) */
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
          min-width:0 !important;
      }}
      /* 카메라 아이콘 버튼(검색창 오른쪽, 정사각 알약형) */
      div[data-testid="column"]:nth-of-type(2) div.stButton > button {{
          border-radius:50%; height:48px; width:48px; min-height:48px;
          padding:0; border:2px solid #a9dcc4; background:#ffffff;
      }}
      div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {{
          border-color:{ACCENT_GREEN}; background:#f0fbf5;
      }}
      div[data-testid="column"]:nth-of-type(2) div.stButton > button span {{
          font-size:1.4rem; color:#1f2933;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _render_hero(big: bool):
    """SR oint 로고 + 타이틀 히어로."""
    uri = _logo_data_uri()
    title_size = "3rem" if big else "1.9rem"
    logo_w = 230 if big else 96
    st.markdown(
        f"<div class='sr-brand' style='font-size:{title_size}'>"
        f"<span class='sr'>SR</span> <span class='oint'>oint</span></div>",
        unsafe_allow_html=True,
    )
    if uri:
        st.markdown(
            f"<img class='sr-logo' src='{uri}' width='{logo_w}'/>",
            unsafe_allow_html=True,
        )
    if big:
        st.markdown(
            "<div class='sr-tagline'>연고를 이름으로 검색하거나 "
            "사진으로 촬영하세요</div>",
            unsafe_allow_html=True,
        )


def _render_full_guide():
    """환자 설명서 전체 안내(전용 화면용)."""
    st.markdown("### 📖 환자 설명서 (전체 안내)")
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


# ─────────────────────────────────────────────
#  화면 상태
# ─────────────────────────────────────────────
if "show_camera" not in st.session_state:
    st.session_state["show_camera"] = False
if "view" not in st.session_state:
    st.session_state["view"] = "home"

# 환자 설명서 전용 화면
if st.session_state["view"] == "guide":
    if st.button("← 돌아가기", key="guide_back"):
        st.session_state["view"] = "home"
        st.rerun()
    _render_full_guide()
    st.stop()

current_q = st.session_state.get("search_box", "").strip()
_render_hero(big=not current_q)

# 검색줄: 입력창 + 카메라 아이콘(한 줄)
c_in, c_cam = st.columns([5, 1])
with c_in:
    q = st.text_input(
        "검색어", key="search_box", label_visibility="collapsed",
        placeholder="검색어를 입력하세요",
    )
with c_cam:
    if st.button(":material/photo_camera:", key="cam_toggle",
                 help="약 상자 촬영으로 검색"):
        st.session_state["show_camera"] = not st.session_state["show_camera"]

# 검색창 바로 아래: 환자 설명서 버튼
if st.button("📖 환자 설명서 (전체 안내)", key="open_guide",
             use_container_width=True):
    st.session_state["view"] = "guide"
    st.rerun()

# 카메라(OCR) 영역
if st.session_state["show_camera"]:
    if not ocr.is_configured():
        st.info("카메라 인식(OCR)을 쓰려면 관리자가 Vision API 키를 설정해야 합니다. "
                "지금은 위 검색창에 이름을 직접 입력해 주세요.")
    else:
        st.caption("아래 버튼을 눌러 약 상자를 촬영하거나 사진을 선택하세요. "
                   "(제품명이 잘 보이게 찍어 주세요)")
        uploaded = st.file_uploader(
            "사진 촬영 또는 선택", type=["jpg", "jpeg", "png"],
            key="cam_file", label_visibility="collapsed")
        if uploaded is not None:
            st.image(uploaded, use_container_width=True)
            with st.spinner("글자 인식 중..."):
                try:
                    text = ocr.ocr_text(uploaded.getvalue())
                except ocr.OCRError as e:
                    text = ""
                    st.error(f"인식 실패: {e}")
            if text:
                cands = core.match_products_from_text(ROWS, text)
                if cands:
                    st.markdown("**인식된 후보 — 눌러서 검색**")
                    for cand in cands:
                        if st.button(f"🔍 {cand}", key=f"cand_{cand}"):
                            st.session_state["search_box"] = cand
                            st.session_state["show_camera"] = False
                            st.rerun()
                else:
                    st.warning("일치하는 약을 찾지 못했습니다. "
                               "아래 인식된 글자를 참고해 직접 검색해 보세요.")
                with st.expander("인식된 전체 글자 보기"):
                    st.code(text, language=None)

q_stripped = q.strip()

# 분류 필터: 검색어가 있을 때만 결과 위에 노출
if q_stripped:
    cat_label = st.selectbox("분류 필터", list(FILTER_OPTIONS.keys()), index=0)
    cat_filter = FILTER_OPTIONS[cat_label]
else:
    cat_filter = ""

res = core.search_ointments(ROWS, q_stripped, cat_filter)

# 검색 요약 (스테로이드 등급 안내)
grades = sorted(
    {int(r["등급_int"]) for r in res if r.get("등급_int") is not None}
    | {int(r["복합스테로이드등급"]) for r in res
       if r.get("복합스테로이드등급") is not None}
)
if q_stripped and grades:
    txt = ", ".join(
        f"{g}등급({core.GRADE_INFO.get(g, ('', ''))[0]})" for g in grades)
    st.success(f"'{q_stripped}' → 스테로이드 {txt}")

# 검색어가 있을 때만 결과를 노출(시작 화면을 깔끔하게)
if q_stripped:
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

# 면책 문구(항상 작게 표시)
st.caption(core.PATIENT_GUIDE["메타"]["면책"])
