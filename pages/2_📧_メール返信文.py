import streamlit as st

from utils.gemini_client import generate_text
from utils.ui import model_selector, require_api_key, temperature_slider

st.set_page_config(page_title="メール返信文作成", page_icon="📧", layout="wide")
st.title("📧 メール返信文作成")
st.caption("受信したメールの内容を貼り付けると、返信文の案を作成します。")

require_api_key()
model = model_selector()
temperature = temperature_slider(default=0.7)

with st.form("mail_form"):
    received_mail = st.text_area("受信したメールの本文", height=200, placeholder="返信したいメールの本文を貼り付けてください")
    intent = st.text_area("返信で伝えたいこと（要点・箇条書きでOK）", height=120, placeholder="例：来週の打ち合わせは火曜14時で問題ない旨を伝えたい。資料は前日までに送付する。")
    relationship = st.selectbox("相手との関係性", ["社外の取引先", "社内の上司・先輩", "社内の同僚・後輩", "初めてやり取りする相手", "親しい間柄"])
    politeness = st.selectbox("文体", ["丁寧なビジネス敬語", "ややカジュアルな丁寧語", "フランクな話し言葉"])
    submitted = st.form_submit_button("返信文を生成する", type="primary")

if submitted:
    if not intent.strip():
        st.warning("返信で伝えたい内容を入力してください。")
    else:
        prompt = f"""あなたは優秀なビジネスアシスタントです。以下の情報をもとに、メールの返信文を作成してください。

# 受信したメールの本文
{received_mail if received_mail.strip() else "（本文の引用なし。新規メールとして作成）"}

# 返信で伝えたい要点
{intent}

# 相手との関係性
{relationship}

# 文体
{politeness}

# 出力形式
- 件名（Re: の形式）
- 宛名
- 本文（挨拶、要点への返答、結びの挨拶を含む）
- 署名欄（「〇〇」のようなプレースホルダーで構いません）
をそのまま使えるメール文面として出力してください。"""

        with st.spinner("返信文を生成しています..."):
            try:
                result = generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
            else:
                st.markdown("### 生成結果")
                st.markdown(result)
                st.text_area("コピー用テキスト", value=result, height=350)
