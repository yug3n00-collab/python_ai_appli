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


def get_api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY")


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
            "GEMINI_API_KEY が設定されていません。.env ファイルに設定してください。"
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
