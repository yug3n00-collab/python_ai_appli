# CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) に向けたガイドです。

## このアプリについて

Streamlit と Gemini API（`google-genai` SDK）で作られた、個人用のAIライティングツールです。データベースも認証もなく、すべてローカルで `.env` のAPIキーを使って動作します。

## コマンド

```
pip install -r requirements.txt   # 依存関係のインストール
streamlit run Home.py             # アプリの起動（マルチページ構成。各機能は pages/ 配下から読み込まれる）
```

テスト・リンター・ビルド手順は設定されていません。

### セットアップ
APIキーは**アプリ起動後にサイドバーの入力欄から直接入力**します（`utils/ui.api_key_input`）。入力値は `st.session_state[API_KEY_SESSION_KEY]` に保持され、同一セッション内の全ページで共有されます（ファイルには保存されません）。任意で `.env.example` を `.env` にコピーして `GEMINI_API_KEY=...` を設定しておくと、入力欄が空のときのフォールバックとして自動で読み込まれます（`.env` は `.gitignore` 対象）。各機能ページではAPIキーが未設定の場合、案内を表示して `st.stop()` で処理を止めます（`utils/ui.require_api_key` 参照）。

## アーキテクチャ

**Streamlitのマルチページアプリです。** `Home.py` がエントリーポイント（トップページ）で、各AI機能は `pages/` 配下に1ファイルずつ配置されています。ファイル名は Streamlit の規約に従い `番号_絵文字_名前.py` の形式（先頭の番号がサイドバーの並び順、絵文字がナビゲーションのアイコンになります）。

**共通処理は `utils/` にまとめており、各ページで重複させない構成になっています：**
- `utils/gemini_client.py` — Gemini API とやり取りする唯一の場所。`DEFAULT_MODEL`/`MODEL_OPTIONS` を保持し、APIキーは `st.session_state`（ブラウザ入力）を優先し無ければ `python-dotenv` 経由の環境変数 `GEMINI_API_KEY` をフォールバックとして読み込み（`get_api_key()`）、`st.cache_resource` で `genai.Client` をキャッシュし、各ページから呼び出される `generate_text(prompt, system_instruction=None, model=..., temperature=...)` を提供します（戻り値は単純な文字列）。
- `utils/ui.py` — 全ての機能ページで使われる共通UI部品。`api_key_input()`（サイドバーのAPIキー入力欄。`require_api_key()` と `Home.py` から呼ばれる）、`require_api_key()`（入力欄を表示しキー未設定時は案内＋`st.stop()`）、`model_selector()`（`MODEL_OPTIONS` からモデルIDを返すサイドバーのドロップダウン）、`temperature_slider(default)`（サイドバーの創造性スライダー）。

**ページの作り方は統一されたパターンに従っています。** 新機能を追加する際は、既存ページ（単純な単一出力の機能なら `pages/3_📄_文章要約.py`、複数パターン生成の機能なら `pages/6_📱_SNS投稿文作成.py`）をコピーして使うのが手早いです：
1. `st.set_page_config(...)` とタイトル・キャプション
2. `require_api_key()` の呼び出し、続けて `model = model_selector()`、`temperature = temperature_slider(default=...)`
3. その機能の入力項目（テキストエリア、セレクトボックス、スライダーなど）を集める `st.form(...)`、最後に `st.form_submit_button`
4. 送信時の処理：フォームの入力値を埋め込んだ日本語のプロンプト文字列を組み立て（任意項目には `"（指定なし）"` のようなフォールバックを用意）、`try/except` と `st.spinner` の中で `generate_text(prompt, model=model, temperature=temperature)` を呼び出し、結果を `st.markdown` とコピー用の `st.text_area` で表示する

新機能を追加する場合は、`pages/` に次の連番のファイルを追加し、`Home.py` のMarkdown内にある機能一覧の表にも項目を追加してください。それ以外に独立したルーティング・登録の仕組みはありません。

## 補足
- UIの文言と生成プロンプトはすべて日本語です。新しいページを作る際もこの方針に合わせてください。
- `temperature` のデフォルト値はタスクの性質によって意図的に変えています（要約・翻訳・校正など忠実性が重要なタスクは低め `~0.3`、ブログ記事・SNS投稿・キャッチコピーなど創造性が求められるタスクは高め `~0.9〜1.1`）。
