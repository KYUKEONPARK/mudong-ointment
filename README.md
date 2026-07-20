# SR oint — 시판 연고 분류 조회기 (웹/모바일)

피부 외용제(연고·크림·로션)를 성분·제품명으로 검색하거나 **약 상자를 카메라로 촬영**해 찾고, 스테로이드 등급과 환자 설명을 확인하는 웹앱입니다. 개인정보·외부 DB는 없습니다. (카메라 인식을 쓸 때만 Vision API 키가 필요합니다.)

## 구성

| 파일 | 용도 |
|---|---|
| `oint_core.py` | 데이터·검색·환자설명·OCR 매칭 로직 (데스크톱 `oint.py`와 공유) |
| `oint_app.py` | Streamlit 웹앱 (SR oint 시작 화면 · 모바일) |
| `ocr.py` | 카메라 사진 OCR (Google Cloud Vision REST) |
| `assets/logo.png` | 시작 화면 로고 |
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
4. Deploy. (텍스트 검색만 쓸 거면 Secrets 없이도 동작합니다.)
5. 생성된 주소(예: `https://mudong-ointment.streamlit.app`)를 휴대폰에서 열거나 공유합니다.

## 카메라 인식(OCR) 설정 — 선택

시작 화면의 카메라 버튼(📷)으로 약 상자를 촬영해 검색하려면 **Google Cloud Vision API 키**가 필요합니다. 키가 없으면 카메라 버튼은 안내만 뜨고, 텍스트 검색은 정상 동작합니다.

1. Google Cloud Console → 기존(또는 새) 프로젝트에서 **Cloud Vision API**를 사용 설정합니다.
2. **API 및 서비스 → 사용자 인증 정보 → API 키 만들기**로 키를 발급합니다. (권장: 키 제한에서 Vision API만 허용)
3. Streamlit Cloud 앱 → **Settings → Secrets** 에 아래 한 줄을 넣고 저장합니다.

```toml
gcp_vision_api_key = "발급받은_API_키"
```

4. 로컬에서 테스트하려면 `oint_web/.streamlit/secrets.toml`에 같은 내용을 넣습니다. (이 파일은 `.gitignore`로 커밋되지 않습니다. **API 키를 코드나 깃에 절대 넣지 마세요.**)

> 촬영 → Vision OCR로 글자 인식 → 인식된 텍스트에서 제품명 후보를 뽑아 버튼으로 보여주고, 누르면 그 이름으로 검색합니다. 일치 후보가 없으면 인식된 전체 글자를 보고 직접 검색할 수 있습니다.

## 인쇄

- 웹/모바일에서는 상세 화면의 **환자 안내문 복사**(코드 상자 우측 상단 복사 아이콘) 후 붙여넣거나, 브라우저 기본 인쇄를 사용하세요.
- 블루투스 프린터로 직접 출력하는 기능은 데스크톱 앱(`oint.py`)에만 있습니다.

## 데이터 수정

`oint_core.py`의 `OINTMENT_DATA`·`PATIENT_GUIDE`·`PATIENT_QNA`를 수정하면 데스크톱·웹 양쪽에 함께 반영됩니다.
