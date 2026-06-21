import logging

import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="キャッチコピー・タイトル生成", page_icon="💡", layout="wide")
st.title("💡 キャッチコピー・タイトル生成")
st.caption("内容や訴求ポイントを入力すると、タイトルやキャッチコピーの候補を複数生成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=1.1)

with st.form("catchcopy_form"):
    purpose = st.selectbox("用途", ["記事・コンテンツのタイトル", "広告・宣伝のキャッチコピー", "商品・サービスのキャッチフレーズ", "イベント・企画のタイトル"])
    subject = st.text_input("対象（商品名・記事のテーマなど）", placeholder="例：オーガニック素材を使った新作スキンケアクリーム")
    appeal_points = st.text_area("訴求したいポイント・特徴（箇条書きでOK）", height=120, placeholder="例：肌に優しい、保湿力が高い、忙しい人でも続けやすいシンプルケア")
    target = st.text_input("ターゲット層（任意）", placeholder="例：30代の敏感肌に悩む女性")
    style = st.selectbox("方向性", ["インパクト重視で印象的に", "信頼感・安心感を伝える", "親しみやすくキャッチーに", "高級感・上質感を演出する", "好奇心を刺激する"])
    num_patterns = st.slider("生成する候補数", min_value=3, max_value=10, value=5)
    submitted = st.form_submit_button("候補を生成する", type="primary")

if submitted:
    if not subject.strip():
        st.warning("対象（商品名・テーマなど）を入力してください。")
    else:
        prompt = f"""あなたは優秀なコピーライターです。以下の条件で「{purpose}」の候補を{num_patterns}個作成してください。

# 対象
{subject}

# 訴求したいポイント・特徴
{appeal_points if appeal_points.strip() else "（指定なし）"}

# ターゲット層
{target if target.strip() else "（指定なし）"}

# 方向性
{style}

# 出力形式
番号付きリストで{num_patterns}個の候補を提示し、それぞれ簡単に「狙い・意図」を一言添えてください。"""

        with st.spinner("候補を生成しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception:
                logging.exception("テキスト生成に失敗しました")
                st.error("生成中にエラーが発生しました。APIキーや入力内容をご確認のうえ、再度お試しください。")
            else:
                st.markdown("### 生成結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=350)
