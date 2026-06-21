import streamlit as st

from utils.gemini_client import is_configured

st.set_page_config(
    page_title="AIライティングツール",
    page_icon="✍️",
    layout="wide",
)

st.title("✍️ AIライティングツール")
st.caption("Gemini API を使った、個人用のオールインワン文章作成支援アプリです。")

if is_configured():
    st.success("Gemini API キーが設定されています。左側のメニューから機能を選んでください。")
else:
    st.warning(
        "Gemini API キーが設定されていません。\n\n"
        "プロジェクト直下に `.env` ファイルを作成し、"
        "`GEMINI_API_KEY=あなたのAPIキー` の形式で設定してください。"
        "（`.env.example` を参考にしてください）"
    )

st.markdown("## 利用できる機能")
st.markdown(
    """
左のサイドバーから、以下の機能を選んで利用できます。

| 機能 | 説明 |
| --- | --- |
| 📝 ブログ記事作成 | テーマやキーワードからブログ記事の下書きを生成します |
| 📧 メール返信文 | 受信したメールの内容から返信文の案を作成します |
| 📄 文章要約 | 長文を指定した長さ・トーンで要約します |
| 🎥 配信概要欄作成 | ライブ配信・動画の概要欄やタイトル案を作成します |
| ✏️ 校正・リライト | 誤字脱字のチェックや、文体・トーンを変えたリライト案を提示します |
| 📱 SNS投稿文作成 | X（旧Twitter）やInstagramなどの投稿文を複数パターン生成します |
| 💡 キャッチコピー・タイトル生成 | 記事タイトルや広告コピーの候補を複数生成します |
| 🌐 翻訳 | 日本語と外国語の間で文章を翻訳します |
"""
)

st.info("各ページの生成結果はそのまま編集・コピーして利用できます。", icon="💡")
