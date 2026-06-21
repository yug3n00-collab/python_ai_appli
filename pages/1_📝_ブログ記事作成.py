import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="ブログ記事作成", page_icon="📝", layout="wide")
st.title("📝 ブログ記事作成")
st.caption("テーマやキーワードを入力すると、ブログ記事の下書きを生成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.9)

with st.form("blog_form"):
    theme = st.text_input("記事のテーマ・タイトル案", placeholder="例：在宅ワークの集中力を高める5つの工夫")
    keywords = st.text_input("含めたいキーワード（カンマ区切り、任意）", placeholder="例：在宅勤務, 集中力, 生産性")
    target = st.text_input("想定読者（任意）", placeholder="例：在宅で働き始めたばかりの20代社会人")
    tone = st.selectbox("文体・トーン", ["丁寧でやさしい", "フレンドリーでカジュアル", "専門的で論理的", "ユーモアを交えた"])
    length = st.select_slider("おおよその文字数", options=["短め（800字程度）", "標準（1500字程度）", "長め（3000字程度）"], value="標準（1500字程度）")
    submitted = st.form_submit_button("記事を生成する", type="primary")

if submitted:
    if not theme.strip():
        st.warning("記事のテーマを入力してください。")
    else:
        prompt = f"""あなたは経験豊富なブログライターです。以下の条件でブログ記事の下書きを作成してください。

# テーマ
{theme}

# 含めたいキーワード
{keywords if keywords.strip() else "（指定なし）"}

# 想定読者
{target if target.strip() else "（指定なし）"}

# 文体・トーン
{tone}

# 分量の目安
{length}

# 出力形式
- 読者の興味を引く見出し（タイトル）を1つ
- 導入文
- 複数の見出し（##）で構成された本文
- まとめ
の構成で、Markdown形式で出力してください。"""

        with st.spinner("記事を生成しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 生成結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=400)
