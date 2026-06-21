# ✍️ AIライティングツール

Streamlit と Gemini API（[`google-genai`](https://pypi.org/project/google-genai/) SDK）で作った、個人用のオールインワン文章作成支援アプリです。
データベースも認証もなく、すべてローカルで `.env` のAPIキーを使って動作します。

## 主な機能

左のサイドバーから、以下の機能を選んで利用できます。生成結果はそのまま編集・コピーして使えます。

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

利用モデルは Gemini 2.5 Flash（高速・バランス型）と Gemini 2.5 Pro（高品質・低速）を各ページのサイドバーから切り替えられます。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 起動

```bash
streamlit run Home.py
```

ブラウザが自動で開きます。Windows では同梱の `起動.bat` をダブルクリックしても起動できます（パスは環境に合わせて調整してください）。

### 3. APIキーの入力

[Google AI Studio](https://aistudio.google.com/apikey) で取得した Gemini API キーを、
アプリ起動後に**サイドバーの「Gemini API キー」欄に直接入力**してください。

> 入力したキーはそのブラウザのセッション内にのみ保持され、サーバーやファイルには保存されません。
> （タブを閉じる／リロードすると再入力が必要です。）
>
> 毎回の入力を省きたい場合は、プロジェクト直下に `.env` を作成して
> `GEMINI_API_KEY=あなたのAPIキー` を記入しておくと、起動時に自動で読み込まれます
> （`.env.example` を参照。`.env` は `.gitignore` 対象なのでコミットされません）。

## プロジェクト構成

```
.
├── Home.py                 # エントリーポイント（トップページ）
├── pages/                  # 各AI機能（Streamlit マルチページ規約: 番号_絵文字_名前.py）
├── utils/
│   ├── gemini_client.py    # Gemini API とやり取りする唯一の場所
│   └── ui.py               # 共通UI部品（APIキー確認・モデル選択・温度スライダー）
├── requirements.txt
├── .env.example
└── .claude/skills/security-check/   # Streamlit/LLM アプリ向けセキュリティレビュー用 Claude Code スキル
```

- **共通処理は `utils/` に集約**しており、各ページで重複させない構成です。Gemini API の呼び出しは `utils/gemini_client.py` の `generate_text()` に一本化されています。
- **温度（temperature）のデフォルト値はタスクの性質によって変えています。** 要約・翻訳・校正など忠実性が重要なタスクは低め（`~0.3`）、ブログ記事・SNS投稿・キャッチコピーなど創造性が求められるタスクは高め（`~0.9〜1.1`）です。
- 新機能を追加する際は、既存ページをコピーして `pages/` に次の連番のファイルを追加し、`Home.py` の機能一覧表に項目を追加します。詳細は [`CLAUDE.md`](./CLAUDE.md) を参照してください。

## 同梱のセキュリティレビュースキル

`.claude/skills/security-check/` には、Streamlit + LLM（Gemini / OpenAI / Claude など）アプリを対象とした
[Claude Code](https://claude.com/claude-code) 用のセキュリティレビュースキルを同梱しています。
シークレット漏洩・プロンプトインジェクション・出力まわり（XSS / `unsafe_allow_html`）・依存関係の脆弱性を重点的に確認し、
重大度別の所見レポートと修正提案を出力します。

## 技術スタック

- [Streamlit](https://streamlit.io/) — マルチページUI
- [Gemini API](https://ai.google.dev/) / [`google-genai`](https://pypi.org/project/google-genai/) SDK
- [python-dotenv](https://pypi.org/project/python-dotenv/) — APIキーの読み込み
