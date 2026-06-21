"""各ページで共通して使う UI 部品。"""
import streamlit as st

from utils.gemini_client import DEFAULT_MODEL, MODEL_OPTIONS, is_configured


def require_api_key() -> None:
    """API キー未設定の場合は警告を表示してページの実行を止める。"""
    if not is_configured():
        st.error(
            "GEMINI_API_KEY が設定されていません。\n\n"
            "プロジェクト直下に `.env` ファイルを作成し、"
            "`GEMINI_API_KEY=あなたのAPIキー` の形式で設定してください。"
        )
        st.stop()


def model_selector() -> str:
    """サイドバーにモデル選択 UI を表示し、選択されたモデル ID を返す。"""
    with st.sidebar:
        st.divider()
        label = st.selectbox(
            "使用するモデル",
            options=list(MODEL_OPTIONS.keys()),
            index=0,
            help="高品質な出力が欲しい場合は Pro を、速度重視の場合は Flash を選んでください。",
        )
    return MODEL_OPTIONS.get(label, DEFAULT_MODEL)


def temperature_slider(default: float = 0.9) -> float:
    """サイドバーに創造性（temperature）調整スライダーを表示する。"""
    with st.sidebar:
        return st.slider(
            "創造性（temperature）",
            min_value=0.0,
            max_value=1.5,
            value=default,
            step=0.1,
            help="数値が高いほど自由で多様な文章になり、低いほど堅実で一貫した文章になります。",
        )
