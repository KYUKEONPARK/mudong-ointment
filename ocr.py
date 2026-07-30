# -*- coding: utf-8 -*-
"""카메라 사진 OCR (Google Cloud Vision REST API).

- API 키는 Streamlit secrets(`gcp_vision_api_key`)에서만 읽는다. 코드/깃에 키를 넣지 않는다.
- 키가 없으면 `is_configured()` 가 False. 이 경우 앱은 텍스트 검색만 정상 동작.
"""

from __future__ import annotations

import base64

import requests

try:
    import streamlit as st
except Exception:  # streamlit 밖(테스트 등)에서도 import 가능하게
    st = None

VISION_URL = "https://vision.googleapis.com/v1/images:annotate"
_TIMEOUT = 30


class OCRError(Exception):
    """OCR 처리 중 발생한 사용자 안내용 오류."""


def _api_key():
    """secrets에서 Vision API 키를 읽는다. 없으면 None."""
    if st is None:
        return None
    try:
        key = st.secrets.get("gcp_vision_api_key", "")
    except Exception:
        return None
    key = (key or "").strip()
    return key or None


def is_configured() -> bool:
    """Vision API 키가 설정되어 있으면 True."""
    return _api_key() is not None


def ocr_text(image_bytes: bytes) -> str:
    """이미지 바이트에서 인식된 전체 텍스트를 반환한다.

    실패 시 OCRError 발생. 텍스트가 없으면 빈 문자열.
    """
    key = _api_key()
    if not key:
        raise OCRError("Vision API 키가 설정되지 않았습니다.")

    payload = {
        "requests": [
            {
                "image": {"content": base64.b64encode(image_bytes).decode()},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["ko", "en"]},
            }
        ]
    }

    # 주의: requests 예외 원문에는 API 키가 포함된 URL이 들어가므로
    # 사용자에게 보여줄 메시지에 예외 내용을 절대 그대로 담지 않는다.
    try:
        resp = requests.post(f"{VISION_URL}?key={key}", json=payload,
                             timeout=_TIMEOUT)
    except requests.Timeout as e:
        raise OCRError("응답이 늦어지고 있습니다. 잠시 후 다시 시도해 주세요.") from e
    except requests.RequestException as e:
        raise OCRError("네트워크 오류가 발생했습니다. 연결 상태를 확인하고 "
                       "다시 시도해 주세요.") from e

    if resp.status_code != 200:
        raise OCRError(f"이미지 인식 서비스 오류(코드 {resp.status_code})가 "
                       "발생했습니다. 잠시 후 다시 시도해 주세요.")

    # 캡티브 포털 등이 200으로 비정상 본문을 돌려줄 수 있어 파싱도 감싼다
    try:
        data = resp.json()
        r0 = (data.get("responses") or [{}])[0]
        if "error" in r0 and r0["error"]:
            raise OCRError(r0["error"].get("message", "인식에 실패했습니다."))

        fta = r0.get("fullTextAnnotation")
        if fta and fta.get("text"):
            return fta["text"].strip()
        tas = r0.get("textAnnotations")
        if tas:
            return (tas[0].get("description") or "").strip()
        return ""
    except OCRError:
        raise
    except Exception as e:
        raise OCRError("인식 결과를 처리하지 못했습니다. 다시 시도해 주세요.") from e
