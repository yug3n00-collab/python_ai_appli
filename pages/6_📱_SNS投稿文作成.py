import logging

import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="SNS投稿文作成", page_icon="📱", layout="wide")
st.title("📱 SNS投稿文作成")
st.caption("伝えたい内容を入力すると、SNSに投稿できる文章を複数パターン生成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=1.0)

with st.form("sns_form"):
    platform = st.selectbox("投稿先のSNS", ["X（旧Twitter）", "Instagram", "Threads", "Facebook", "LinkedIn"])
    content = st.text_area("投稿で伝えたい内容", height=150, placeholder="例：新しく出したオリジナルグッズの紹介。発売日と購入方法も伝えたい。")
    tone = st.selectbox("雰囲気・トーン", ["フレンドリーで明るい", "丁寧でフォーマル", "ユーモラスで面白い", "クールで洗練された", "情熱的で熱量のある"])
    use_emoji = st.checkbox("絵文字を使う", value=True)
    use_hashtags = st.checkbox("ハッシュタグ案を含める", value=True)
    num_patterns = st.slider("生成するパターン数", min_value=1, max_value=5, value=3)
    submitted = st.form_submit_button("投稿文を生成する", type="primary")

if submitted:
    if not content.strip():
        st.warning("投稿で伝えたい内容を入力してください。")
    else:
        extra_instructions = []
        if use_emoji:
            extra_instructions.append("適度に絵文字を使用すること。")
        else:
            extra_instructions.append("絵文字は使用しないこと。")
        if use_hashtags:
            extra_instructions.append("各案の最後に関連するハッシュタグを3〜5個程度添えること。")
        else:
            extra_instructions.append("ハッシュタグは不要。")

        platform_limits = {
            "X（旧Twitter）": "1投稿あたり全角140文字程度に収まる長さにすること。",
            "Instagram": "やや長めの説明文でも構わないが、読みやすく改行を入れること。",
            "Threads": "1投稿あたり全角500文字程度に収まる長さにすること。",
            "Facebook": "丁寧でやや長めの文章でも構わない。",
            "LinkedIn": "ビジネス的に節度のある、信頼感のある文章にすること。",
        }

        prompt = f"""あなたはSNS運用に詳しいコピーライターです。以下の条件でSNS投稿文を{num_patterns}パターン作成してください。

# 投稿先のSNS
{platform}
（{platform_limits.get(platform, "")}）

# 伝えたい内容
{content}

# 雰囲気・トーン
{tone}

# その他の指示
{chr(10).join(f"- {item}" for item in extra_instructions)}

# 出力形式
「パターン1」「パターン2」のように見出しを付けて、それぞれの投稿文をそのまま使える形で提示してください。"""

        with st.spinner("投稿文を生成しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception:
                logging.exception("テキスト生成に失敗しました")
                st.error("生成中にエラーが発生しました。APIキーや入力内容をご確認のうえ、再度お試しください。")
            else:
                st.markdown("### 生成結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=350)
