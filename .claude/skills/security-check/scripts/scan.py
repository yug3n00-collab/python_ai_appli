#!/usr/bin/env python3
"""Streamlit + LLM アプリ向けの軽量セキュリティスキャナ。

機械的に検出しやすい項目だけを一括で洗い出し、レビューの出発点を作る。
- ハードコードされたAPIキーらしき文字列（Google / OpenAI / Anthropic）
- .env が存在するのに .gitignore に入っていない
- .streamlit/secrets.toml がコミット対象になっている恐れ
- st.markdown(..., unsafe_allow_html=True) / components.v1.html / st.html の使用
- requirements のバージョン非固定
- eval / exec / os.system / subprocess / pickle.load の使用

このスクリプトは「当たりをつける」ためのもの。ヒットは必ず実コードで確認すること。
ネットワークやインストールは行わない（CVE照合は別途 pip-audit を提案）。

使い方:
    python scan.py <対象ディレクトリ>   # 省略時はカレントディレクトリ
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# --- 検出パターン -----------------------------------------------------------

# APIキーらしき値の直書き。キー名だけの参照（os.environ.get(...)）は拾わないよう、
# 実際のキー形状にマッチさせる。
SECRET_VALUE_PATTERNS = [
    ("Google APIキーらしき値", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("OpenAI APIキーらしき値", re.compile(r"sk-(?:proj-)?[0-9A-Za-z_\-]{20,}")),
    ("Anthropic APIキーらしき値", re.compile(r"sk-ant-[0-9A-Za-z_\-]{20,}")),
    (
        "キーらしき変数への文字列直書き",
        re.compile(r"""(?i)(api_key|secret|token|password)\s*=\s*["'][^"'\s]{12,}["']"""),
    ),
]

# 出力・XSS 面
HTML_PATTERNS = [
    ("unsafe_allow_html=True", re.compile(r"unsafe_allow_html\s*=\s*True")),
    ("components.v1.html / st.html", re.compile(r"(components\.v1\.html|st\.html)\s*\(")),
]

# 危険な実行系
DANGEROUS_PATTERNS = [
    ("eval(", re.compile(r"\beval\s*\(")),
    ("exec(", re.compile(r"\bexec\s*\(")),
    ("os.system(", re.compile(r"\bos\.system\s*\(")),
    ("subprocess", re.compile(r"\bsubprocess\.")),
    ("pickle.load", re.compile(r"\bpickle\.load")),
]

# キー名だけのプレースホルダ（誤検知になりやすいので除外用）
PLACEHOLDER_HINTS = re.compile(r"(?i)(your_?api_?key|xxxx|placeholder|example|<.*>|here)")

SCAN_EXTENSIONS = {".py", ".toml", ".env", ".txt", ".cfg", ".ini", ".json", ".yaml", ".yml"}
# .claude / .agents はスキル・ツール本体でアプリ本体ではないため除外（自己参照ノイズを防ぐ）
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache",
    ".claude", ".agents",
}


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            # .env / .env.example などは拡張子判定では拾えないので名前でも許可
            if p.suffix in SCAN_EXTENSIONS or p.name.startswith(".env"):
                yield p


def read_lines(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def scan_content(root: Path):
    findings = []  # (category, label, relpath, lineno, line)
    for path in iter_files(root):
        rel = path.relative_to(root)
        for i, line in enumerate(read_lines(path), start=1):
            for label, pat in SECRET_VALUE_PATTERNS:
                if pat.search(line) and not PLACEHOLDER_HINTS.search(line):
                    findings.append(("シークレット直書きの疑い", label, rel, i, line.strip()))
            for label, pat in HTML_PATTERNS:
                if pat.search(line):
                    findings.append(("出力・XSS", label, rel, i, line.strip()))
            for label, pat in DANGEROUS_PATTERNS:
                if pat.search(line):
                    findings.append(("危険な実行系", label, rel, i, line.strip()))
    return findings


def check_env_gitignore(root: Path):
    notes = []
    gitignore = root / ".gitignore"
    ignored = set()
    if gitignore.exists():
        ignored = {ln.strip() for ln in read_lines(gitignore) if ln.strip()}

    env_files = [p for p in root.glob(".env*") if p.name != ".env.example"]
    real_env = root / ".env"
    if real_env.exists():
        covered = any(pat in ignored for pat in (".env", ".env*", "*.env"))
        if not covered:
            notes.append("⚠ .env が存在するが .gitignore で除外されていない可能性")
        else:
            notes.append("✓ .env は .gitignore で除外されている")
    secrets = root / ".streamlit" / "secrets.toml"
    if secrets.exists():
        covered = any("secrets.toml" in pat for pat in ignored)
        if not covered:
            notes.append("⚠ .streamlit/secrets.toml が存在し .gitignore で除外されていない可能性")
    return notes


def check_requirements(root: Path):
    notes = []
    for fname in ("requirements.txt",):
        f = root / fname
        if not f.exists():
            continue
        unpinned = []
        for ln in read_lines(f):
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("-"):
                continue
            if not re.search(r"[=<>~!]=|@", s):
                unpinned.append(s)
        if unpinned:
            notes.append(f"⚠ {fname}: バージョン非固定の依存 -> {', '.join(unpinned)}")
        else:
            notes.append(f"✓ {fname}: 依存はバージョン指定あり")
    return notes


def main():
    # Windows コンソール（cp932）でも日本語・記号を出せるよう UTF-8 に切り替える
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"# 機械的スキャン結果: {root}\n")

    print("## 設定ファイルのチェック")
    for note in check_env_gitignore(root) + check_requirements(root):
        print(f"- {note}")
    print()

    findings = scan_content(root)
    print("## コードスキャンのヒット（要・実コード確認）")
    if not findings:
        print("- 該当なし")
    else:
        by_cat = {}
        for cat, label, rel, lineno, line in findings:
            by_cat.setdefault(cat, []).append((label, rel, lineno, line))
        for cat, items in by_cat.items():
            print(f"\n### {cat}")
            for label, rel, lineno, line in items:
                snippet = line if len(line) <= 120 else line[:117] + "..."
                print(f"- [{label}] `{rel}:{lineno}`  {snippet}")
    print("\n> 注: これは出発点。各ヒットを実コードで確認し、設計レベルの問題は別途精査すること。")


if __name__ == "__main__":
    main()
