# 시판 연고 분류 조회기 (웹/모바일)

피부 외용제(연고·크림·로션)를 성분·제품명으로 검색하고, 스테로이드 등급과 환자 설명을 확인하는 웹앱입니다. 개인정보·외부 DB·비밀키가 전혀 없어 그대로 공개 배포할 수 있습니다.

## 구성

| 파일 | 용도 |
|---|---|
| `oint_core.py` | 데이터·검색·환자설명 로직 (데스크톱 `oint.py`와 공유) |
| `oint_app.py` | Streamlit 웹앱 (모바일 화면) |
| `requirements.txt` | 의존 패키지 |

> 데스크톱 앱(`../oint.py`, Tkinter)도 이 폴더의 `oint_core.py`를 import 해서 같은 데이터를 씁니다. 데이터는 한 벌만 관리됩니다.

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run oint_app.py
```

브라우저가 자동으로 열립니다(기본 http://localhost:8501). `localhost` 주소는 내 PC에서만 열립니다. 휴대폰에서 보려면 아래 클라우드 배포가 필요합니다.

## 폰에서 보기 (GitHub + Streamlit Community Cloud)

무료로 **공개 링크**를 만드는 방법입니다.

1. 이 폴더를 GitHub 저장소(예: `KYUKEONPARK/mudong-ointment`)에 올립니다.
2. https://share.streamlit.io 로그인 → **New app**.
3. 저장소/브랜치 선택, **Main file path = `oint_app.py`** 지정.
4. Deploy. (Secrets 설정 불필요 — 이 앱은 자격증명을 쓰지 않습니다.)
5. 생성된 주소(예: `https://mudong-ointment.streamlit.app`)를 휴대폰에서 열거나 공유합니다.

## 인쇄

- 웹/모바일에서는 상세 화면의 **환자 안내문 복사**(코드 상자 우측 상단 복사 아이콘) 후 붙여넣거나, 브라우저 기본 인쇄를 사용하세요.
- 블루투스 프린터로 직접 출력하는 기능은 데스크톱 앱(`oint.py`)에만 있습니다.

## 데이터 수정

`oint_core.py`의 `OINTMENT_DATA`·`PATIENT_GUIDE`·`PATIENT_QNA`를 수정하면 데스크톱·웹 양쪽에 함께 반영됩니다.
