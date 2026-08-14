"""コアロジック: 指示テキストのモード判定 → 生成/修正 → デプロイ。

bot.py（Telegram）と test_mock_cycle.py（テスト）の両方から使う。
"""
from typing import Optional

import config
import deployer
import generator
from generator import MODE_APP, MODE_FIX, MODE_RESEARCH
from session import SessionStore

sessions = SessionStore(config.SESSION_FILE)

_FIX_KEYWORDS = (
    "修正", "直して", "なおして", "変えて", "変更", "追加して", "足して",
    "消して", "削除", "調整", "更新して", "アップデート",
)
_RESEARCH_KEYWORDS = (
    "リサーチ", "調べて", "調査", "まとめて", "動向", "比較して", "レポート",
)


def classify(text: str, last_file: Optional[str]) -> str:
    """モード判定。明示プレフィックス > 修正キーワード > リサーチキーワード > アプリ生成。"""
    stripped = text.strip()
    lower = stripped.lower()

    if lower.startswith("/fix"):
        return MODE_FIX
    if lower.startswith("/research"):
        return MODE_RESEARCH
    if lower.startswith("/app"):
        return MODE_APP

    # 修正モードは「直前のファイルがある」場合のみ成立する
    if last_file and any(k in stripped for k in _FIX_KEYWORDS):
        return MODE_FIX
    if any(k in stripped for k in _RESEARCH_KEYWORDS):
        return MODE_RESEARCH
    return MODE_APP


def _strip_prefix(text: str) -> str:
    stripped = text.strip()
    for prefix in ("/fix", "/research", "/app"):
        if stripped.lower().startswith(prefix):
            return stripped[len(prefix):].strip()
    return stripped


def handle_instruction(chat_id, text: str) -> dict:
    """1つの指示を処理して結果を返す。

    Returns: {"mode": str, "filename": str, "url": str}
    """
    last_file = sessions.get_last_file(chat_id)
    mode = classify(text, last_file)
    instruction = _strip_prefix(text)

    if mode == MODE_FIX:
        if not last_file:
            raise ValueError(
                "修正対象のページがまだありません。先に新規作成の指示を送ってください。"
            )
        filename = generator.fix(last_file, instruction)
        commit_msg = f"mock-studio: fix {filename}"
    else:
        filename = generator.generate(mode, instruction)
        commit_msg = f"mock-studio: add {filename} ({mode})"

    url = deployer.deploy(filename, commit_msg)
    sessions.set_last_file(chat_id, filename)
    return {"mode": mode, "filename": filename, "url": url}
