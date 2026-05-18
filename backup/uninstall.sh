#!/bin/bash
# 00_Shota-all バックアップの解除
# バックアップデータは削除しない（必要なら手動で削除）

set -euo pipefail

PLIST_DST="$HOME/Library/LaunchAgents/com.ueyama.shota-all-backup.plist"

echo "launchd から登録解除..."
launchctl unload "$PLIST_DST" 2>/dev/null || true
rm -f "$PLIST_DST"

echo "解除完了。"
echo ""
echo "バックアップデータは ~/Backups/00_Shota-all-backup/ に残っています。"
echo "不要なら手動で削除してください:"
echo "  rm -rf ~/Backups/00_Shota-all-backup"
