"""環境設定の一元管理。値はすべて .env（gitignore対象）から読み込む。"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# 許可するチャットID（カンマ区切り）。空の場合は全拒否（安全側に倒す）
ALLOWED_CHAT_IDS = {
    s.strip() for s in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if s.strip()
}

# Claude Code CLI
CLAUDE_BIN = os.getenv("CLAUDE_BIN", "claude")
CLAUDE_TIMEOUT_SEC = int(os.getenv("CLAUDE_TIMEOUT_SEC", "1200"))

# 生成物・デプロイ
PAGES_DIR = Path(os.getenv("PAGES_DIR", str(BASE_DIR / "pages")))
REPO_DIR = Path(os.getenv("REPO_DIR", str(BASE_DIR.parent)))  # claude-artifacts リポ
BASE_URL = os.getenv(
    "BASE_URL", "https://major-senzu.github.io/claude-artifacts/mock-studio/pages"
).rstrip("/")

# セッション状態（チャットごとの直前ファイル名）
SESSION_FILE = Path(os.getenv("SESSION_FILE", str(BASE_DIR / "sessions.json")))

# テスト用フラグ
MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1"   # Claude を呼ばずダミーHTML生成
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"       # git commit/push をスキップ
