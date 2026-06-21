import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="配信概要欄作成", page_icon="🎥", layout="wide")
st.title("🎥 ライブ配信・動画概要欄作成")
st.caption("配信や動画の内容を入力すると、概要欄の文章とハッシュタグ案を生成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.9)

with st.form("stream_form"):
    title = st.text_input("配信・動画のタイトル（仮でも可）", placeholder="例：【雑談】最近ハマっているゲームについて語る")
    content = st.text_area("配信・動画の内容（話す内容・見どころなど）", height=180, placeholder="例：新しく始めたゲームの感想、視聴者からの質問コーナー、次回予告など")
    platform = st.selectbox("配信プラットフォーム", ["YouTube Live", "YouTube動画", "Twitch", "ニコニコ生放送", "TikTok LIVE", "その他"])
    tone = st.selectbox("雰囲気・トーン", ["フレンドリーで親しみやすい", "テンション高めで賑やか", "落ち着いた丁寧な雰囲気", "ユーモラスで面白い"])
    include_hashtags = st.checkbox("ハッシュタグ案も生成する", value=True)
    submitted = st.form_submit_button("概要欄を生成する", type="primary")

if submitted:
    if not content.strip():
        st.warning("配信・動画の内容を入力してください。")
    else:
        hashtag_instruction = (
            "概要欄の文章の最後に、関連するハッシュタグを5〜8個程度提案してください。"
            if include_hashtags
            else "ハッシュタグは不要です。"
        )
        prompt = f"""あなたは配信者の運営を支援するアシスタントです。以下の情報をもとに、配信・動画の概要欄の文章を作成してください。

# タイトル（仮）
{title if title.strip() else "（未定）"}

# 配信・動画の内容
{content}

# プラットフォーム
{platform}

# 雰囲気・トーン
{tone}

# 出力内容
1. 視聴者の興味を引くタイトル案を3つ
2. 概要欄に使える紹介文（挨拶、内容紹介、視聴を呼びかける一言を含む）
3. {hashtag_instruction}

Markdown形式で見やすく出力してください。"""

        with st.spinner("概要欄を生成しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 生成結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=350)
