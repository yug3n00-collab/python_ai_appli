import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="文章要約", page_icon="📄", layout="wide")
st.title("📄 文章要約")
st.caption("長い文章を貼り付けると、指定した条件で要約します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.3)

with st.form("summary_form"):
    source_text = st.text_area("要約したい文章", height=300, placeholder="ここに要約したい文章を貼り付けてください")
    style = st.selectbox("要約のスタイル", ["箇条書きで要点を整理", "短い文章で簡潔にまとめる", "見出し付きで構造化してまとめる"])
    length = st.select_slider("要約の長さ", options=["とても短く（3行程度）", "短め（5行程度）", "標準（10行程度）"], value="短め（5行程度）")
    submitted = st.form_submit_button("要約する", type="primary")

if submitted:
    if not source_text.strip():
        st.warning("要約したい文章を入力してください。")
    else:
        prompt = f"""以下の文章を、指定された条件で要約してください。

# 要約のスタイル
{style}

# 要約の長さの目安
{length}

# 要約対象の文章
{source_text}

# 注意事項
- 元の文章の意図やニュアンスを変えないこと
- 重要なポイントを漏らさないこと
- 出力は要約結果のみとすること"""

        with st.spinner("要約しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 要約結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=250)
