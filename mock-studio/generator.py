"""Claude Code CLI をヘッドレス実行して HTML を生成・修正する。"""
import datetime
import subprocess
from pathlib import Path

import config

MODE_RESEARCH = "research"
MODE_APP = "app"
MODE_FIX = "fix"

_RESEARCH_PROMPT = """以下のテーマについてWeb検索でリサーチし、美麗なレポートHTMLを1ファイル作成してください。

テーマ: {instruction}

要件:
- WebSearchツールで最新情報を収集し、末尾に出典URLリストを明記する
- 出力先: カレントディレクトリの {filename}（このファイル1つだけを作成する）
- Tailwind CSS（CDN: https://cdn.tailwindcss.com）を使った読みやすいレポートデザイン
  （ヒーローヘッダー・目次・セクションカード・キーポイントの強調・出典リスト）
- スマホ表示（レスポンシブ）に対応、lang="ja"、日本語で執筆
- 外部ビルド不要・CDNのみで完結する単一HTML

ファイル作成以外の作業（git操作・他ファイルの編集等）は行わないこと。"""

_APP_PROMPT = """以下の指示に基づき、ブラウザ上で実際に動作する単一HTMLのWebアプリモックを作成してください。

指示: {instruction}

要件:
- 出力先: カレントディレクトリの {filename}（このファイル1つだけを作成する）
- Tailwind CSS（CDN: https://cdn.tailwindcss.com）、Lucide Icons（CDN）、Vanilla JS を使用
  （複雑な状態管理が必要な場合のみ Vue/React の CDN 版を使ってよい）
- 外部ビルド不要・CDNのみで完結し、スマホ表示（レスポンシブ）に対応
- lang="ja"、タイトル・UIテキストは日本語
- モックだが主要機能は実際に動作させる（ダミーデータ可）

ファイル作成以外の作業（git操作・他ファイルの編集等）は行わないこと。"""

_FIX_PROMPT = """カレントディレクトリの {filename} を読み、以下の修正指示を反映して同じファイルを上書き更新してください。

修正指示: {instruction}

要件:
- 修正指示に関係しない既存のデザイン・機能・テキストは維持する
- 単一HTML・CDN完結・スマホ対応という構成は崩さない

ファイル編集以外の作業（git操作・他ファイルの編集等）は行わないこと。"""


def make_filename(mode: str) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{mode}-{ts}.html"


def _run_claude(prompt: str) -> None:
    cmd = [
        config.CLAUDE_BIN,
        "-p",
        prompt,
        "--permission-mode",
        "bypassPermissions",
    ]
    result = subprocess.run(
        cmd,
        cwd=str(config.PAGES_DIR),
        capture_output=True,
        text=True,
        timeout=config.CLAUDE_TIMEOUT_SEC,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI failed (exit {result.returncode}): {result.stderr[:500]}"
        )


def _mock_generate(path: Path, mode: str, instruction: str) -> None:
    path.write_text(
        "<!DOCTYPE html>\n"
        '<html lang="ja"><head><meta charset="utf-8">'
        f"<title>MOCK {mode}</title></head>\n"
        f"<body><h1>MOCK ({mode})</h1><p>{instruction}</p></body></html>\n",
        encoding="utf-8",
    )


def _mock_fix(path: Path, instruction: str) -> None:
    html = path.read_text(encoding="utf-8")
    path.write_text(
        html.replace("</body>", f"<p>FIXED: {instruction}</p></body>"),
        encoding="utf-8",
    )


def generate(mode: str, instruction: str) -> str:
    """新規生成（research / app）。生成したファイル名を返す。"""
    config.PAGES_DIR.mkdir(parents=True, exist_ok=True)
    filename = make_filename(mode)
    path = config.PAGES_DIR / filename

    if config.MOCK_MODE:
        _mock_generate(path, mode, instruction)
    else:
        template = _RESEARCH_PROMPT if mode == MODE_RESEARCH else _APP_PROMPT
        _run_claude(template.format(instruction=instruction, filename=filename))

    if not path.exists():
        raise RuntimeError(f"生成に失敗しました: {filename} が作成されていません")
    return filename


def fix(filename: str, instruction: str) -> str:
    """既存ファイルの修正。修正したファイル名を返す。"""
    path = config.PAGES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"修正対象が見つかりません: {filename}")

    if config.MOCK_MODE:
        _mock_fix(path, instruction)
    else:
        _run_claude(_FIX_PROMPT.format(instruction=instruction, filename=filename))
    return filename
