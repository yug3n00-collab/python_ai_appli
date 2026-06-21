import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="校正・リライト", page_icon="✏️", layout="wide")
st.title("✏️ 文章校正・リライト")
st.caption("文章の誤字脱字チェックや、文体・トーンを変えたリライト案を作成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.6)

with st.form("rewrite_form"):
    source_text = st.text_area("校正・リライトしたい文章", height=250, placeholder="ここに文章を貼り付けてください")
    mode = st.radio(
        "実施したい内容",
        ["誤字脱字・文法のチェックのみ", "文体・トーンを変えてリライト", "両方（チェック後にリライト）"],
        horizontal=False,
    )
    target_tone = st.selectbox(
        "リライト後の文体・トーン（リライトする場合）",
        ["より丁寧でフォーマルに", "よりカジュアルで親しみやすく", "より簡潔に", "より説得力のある表現に", "より優しく柔らかい表現に"],
    )
    submitted = st.form_submit_button("実行する", type="primary")

if submitted:
    if not source_text.strip():
        st.warning("文章を入力してください。")
    else:
        if mode == "誤字脱字・文法のチェックのみ":
            task_instruction = (
                "文章中の誤字脱字、文法的な誤り、不自然な表現を指摘し、"
                "「指摘箇所」と「修正案」を対応させて一覧で示したうえで、"
                "最後に修正後の全文を提示してください。"
            )
        elif mode == "文体・トーンを変えてリライト":
            task_instruction = (
                f"元の文章の意味を保ったまま、「{target_tone}」という方向性でリライトしてください。"
                "リライト後の全文を提示し、どのように変更したかのポイントも簡潔に説明してください。"
            )
        else:
            task_instruction = (
                "まず誤字脱字や文法的な誤りを指摘し、それを修正した文章を作成してください。"
                f"続けて、その文章を「{target_tone}」という方向性でリライトし、最終的なリライト後の全文を提示してください。"
            )

        prompt = f"""あなたはプロの校正者・編集者です。以下の文章に対して指示された作業を行ってください。

# 対象の文章
{source_text}

# 実施内容
{task_instruction}

Markdown形式で、見やすく整理して出力してください。"""

        with st.spinner("処理しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=350)
