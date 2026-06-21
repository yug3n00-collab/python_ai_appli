"""各ページで共通して使う UI 部品。"""
import streamlit as st

from utils.gemini_client import (
    API_KEY_SESSION_KEY,
    DEFAULT_MODEL,
    MODEL_OPTIONS,
    is_configured,
)


def api_key_input() -> None:
    """サイドバーに Gemini API キーの入力欄を表示する。

    入力値は st.session_state[API_KEY_SESSION_KEY] に保持され、
    同一セッション内の全ページで共有される（ファイルには保存されない）。
    """
    with st.sidebar:
        st.text_input(
            "Gemini API キー",
            type="password",
            key=API_KEY_SESSION_KEY,
            placeholder="AIza... から始まるキーを入力",
            help=(
                "Google AI Studio（https://aistudio.google.com/apikey）で取得した"
                "API キーを入力してください。入力したキーは生成リクエストの実行にのみ使われ、"
                "アプリのサーバー側セッションに一時的に保持されます"
                "（ファイルやデータベースには保存されず、セッション終了で破棄されます）。"
                "共有端末では使用後にタブを閉じてください。"
            ),
        )


def require_api_key() -> None:
    """サイドバーに入力欄を表示し、API キー未設定ならページの実行を止める。"""
    api_key_input()
    if not is_configured():
        st.info("👈 サイドバーに Gemini API キーを入力すると、この機能を利用できます。")
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
