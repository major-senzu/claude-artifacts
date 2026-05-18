#!/bin/bash
# 00_Shota-all バックアップの初回セットアップ

set -euo pipefail

SCRIPT_DIR="/Users/major/Documents/00_Shota-all/05_automation/backup"
BACKUP_ROOT="/Users/major/Backups/00_Shota-all-backup"
PLIST_SRC="$SCRIPT_DIR/com.ueyama.shota-all-backup.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.ueyama.shota-all-backup.plist"

echo "[1/5] バックアップ先ディレクトリを作成..."
mkdir -p "$BACKUP_ROOT/_logs"

echo "[2/5] backup.sh に実行権限を付与..."
chmod +x "$SCRIPT_DIR/backup.sh"

echo "[3/5] launchd plist をインストール..."
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"

echo "[4/5] launchd に登録（既存があれば再読み込み）..."
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo "[5/5] 初回バックアップを実行（数分かかる場合あり）..."
bash "$SCRIPT_DIR/backup.sh"

echo ""
echo "======================================"
echo "セットアップ完了！"
echo "======================================"
echo "バックアップ先: $BACKUP_ROOT"
echo "実行時刻: 毎日 03:00"
echo "保持期間: 7日分"
echo ""
echo "状況確認:"
echo "  launchctl list | grep shota-all-backup"
echo "  ls -la $BACKUP_ROOT"
echo ""
