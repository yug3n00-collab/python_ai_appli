import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="翻訳", page_icon="🌐", layout="wide")
st.title("🌐 翻訳")
st.caption("文章を入力すると、指定した言語・トーンに翻訳します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.3)

LANGUAGES = ["日本語", "英語", "中国語（簡体字）", "中国語（繁体字）", "韓国語", "フランス語", "ドイツ語", "スペイン語", "ポルトガル語"]

with st.form("translate_form"):
    source_text = st.text_area("翻訳したい文章", height=250, placeholder="ここに翻訳したい文章を入力してください")
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("翻訳元の言語", ["自動検出"] + LANGUAGES)
    with col2:
        target_lang = st.selectbox("翻訳先の言語", LANGUAGES, index=1)
    tone = st.selectbox("翻訳のトーン", ["自然で標準的な訳", "丁寧でフォーマルな訳", "カジュアルで口語的な訳", "ビジネス文書向けの訳"])
    add_notes = st.checkbox("意訳した箇所や言葉のニュアンスについて補足説明を加える", value=False)
    submitted = st.form_submit_button("翻訳する", type="primary")

if submitted:
    if not source_text.strip():
        st.warning("翻訳したい文章を入力してください。")
    else:
        notes_instruction = (
            "翻訳結果の後に、意訳した箇所や訳しにくかった表現について簡潔に補足説明を加えてください。"
            if add_notes
            else "翻訳結果のみを出力し、余計な説明は加えないでください。"
        )
        source_lang_text = "（自動検出してください）" if source_lang == "自動検出" else source_lang

        prompt = f"""あなたはプロの翻訳者です。以下の文章を翻訳してください。

# 翻訳元の言語
{source_lang_text}

# 翻訳先の言語
{target_lang}

# トーン
{tone}

# 翻訳対象の文章
{source_text}

# 指示
{notes_instruction}
原文の意味やニュアンスをできるだけ正確に保つこと。"""

        with st.spinner("翻訳しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 翻訳結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=300)
