# -*- coding: utf-8 -*-
"""촬영 후 검색어 자동 기록 크래시(StreamlitAPIException) 회귀 테스트.

- 버그 재현: text_input(key="search_box") 생성 후 같은 실행에서
  st.session_state["search_box"]를 직접 수정하면 예외가 나야 한다.
- 수정 검증: pending_search 임시 키 + rerun 후 위젯 생성 전 반영 방식은
  예외 없이 검색창 값이 바뀌어야 한다.
실행:  .venv/bin/python _pending_search_test.py
"""

import tempfile
from pathlib import Path

from streamlit.testing.v1 import AppTest

BUGGY = """
import streamlit as st
q = st.text_input("검색어", key="search_box")
if st.button("촬영시뮬"):
    st.session_state["search_box"] = "아드반탄"  # 위젯 생성 후 직접 수정 → 예외
"""

FIXED = """
import streamlit as st
if "pending_search" in st.session_state:
    st.session_state["search_box"] = st.session_state.pop("pending_search")
q = st.text_input("검색어", key="search_box")
if st.button("촬영시뮬"):
    st.session_state["pending_search"] = "아드반탄"
    st.rerun()
"""


def _run(src: str) -> AppTest:
    p = Path(tempfile.mkdtemp()) / "app.py"
    p.write_text(src, encoding="utf-8")
    at = AppTest.from_file(str(p))
    at.run()
    at.button[0].click().run()
    return at


def main():
    buggy = _run(BUGGY)
    assert buggy.exception, "버그 재현 실패: 직접 수정인데 예외가 없음"
    assert "cannot be modified" in buggy.exception[0].message, buggy.exception[0].message
    print("버그 재현 OK:", buggy.exception[0].message[:80], "...")

    fixed = _run(FIXED)
    assert not fixed.exception, f"수정안에서 예외 발생: {fixed.exception}"
    assert fixed.text_input[0].value == "아드반탄", fixed.text_input[0].value
    print("수정 검증 OK: 검색창 값 =", fixed.text_input[0].value)


if __name__ == "__main__":
    main()
    print("ALL PASS")
