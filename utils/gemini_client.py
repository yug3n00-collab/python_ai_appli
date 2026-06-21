"""Gemini API 呼び出しの共通処理をまとめたモジュール。"""
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"
MODEL_OPTIONS = {
    "Gemini 2.5 Flash（高速・バランス型）": "gemini-2.5-flash",
    "Gemini 2.5 Pro（高品質・低速）": "gemini-2.5-pro",
}

# ブラウザで入力された API キーを保持する st.session_state のキー名。
API_KEY_SESSION_KEY = "gemini_api_key"

# 環境変数 GEMINI_API_KEY をフォールバックとして使うかどうか。
# 公開環境（Streamlit Community Cloud 等）では既定で無効。所有者のキーが
# 匿名の利用者に共有され、課金枠を悪用される事故を防ぐため、ローカル開発で
# 明示的に ALLOW_ENV_KEY_FALLBACK=1 を設定したときだけ有効にする。
ALLOW_ENV_KEY_FALLBACK = os.environ.get("ALLOW_ENV_KEY_FALLBACK") == "1"


def get_api_key() -> str | None:
    """ブラウザ（サイドバー）で入力されたキーを使う。

    ALLOW_ENV_KEY_FALLBACK=1 のときのみ、環境変数 GEMINI_API_KEY を
    フォールバックとして使う（ローカル開発向け）。
    """
    key = st.session_state.get(API_KEY_SESSION_KEY)
    if key and key.strip():
        return key.strip()
    if ALLOW_ENV_KEY_FALLBACK:
        env_key = os.environ.get("GEMINI_API_KEY")
        return env_key.strip() if env_key else None
    return None


@st.cache_resource(show_spinner=False)
def _get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def is_configured() -> bool:
    return bool(get_api_key())


def generate_text(
    prompt: str,
    system_instruction: str | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.9,
) -> str:
    """Gemini API にプロンプトを送信し、生成されたテキストを返す。"""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API キーが設定されていません。サイドバーの入力欄にキーを入力してください。"
        )

    client = _get_client(api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        ),
    )
    return response.text or ""
