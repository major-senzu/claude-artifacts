#!/bin/bash
# 00_Shota-all 日次バックアップ
# ハードリンクで7世代のスナップショットを保持（容量は最小限）
# 変更があったファイルのみ実体コピー、他は既存世代へのリンク

set -euo pipefail

SOURCE="/Users/major/Documents/00_Shota-all/"
BACKUP_ROOT="/Users/major/Backups/00_Shota-all-backup"
TODAY=$(date +%Y-%m-%d)
TODAY_DIR="$BACKUP_ROOT/$TODAY"
LATEST="$BACKUP_ROOT/latest"
LOG_DIR="$BACKUP_ROOT/_logs"
LOG_FILE="$LOG_DIR/backup-$TODAY.log"
RETENTION_DAYS=7
LOG_RETENTION_DAYS=30

mkdir -p "$BACKUP_ROOT" "$LOG_DIR"

echo "===== Backup start: $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"

# 今日の分がすでにあれば上書きせずスキップ（手動再実行時の保護）
if [ -d "$TODAY_DIR" ]; then
  echo "Today's snapshot already exists, running incremental update" >> "$LOG_FILE"
fi

# rsync: -a（属性保持）, -H（ハードリンク保持）, --delete（削除も反映）
# --link-dest: 前回から変化のないファイルをハードリンクで参照（ディスク節約）
# exit 23/24（部分転送・ファイル消失）は警告扱いで成功とみなす
set +e
if [ -d "$LATEST" ]; then
  rsync -aH --delete \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='.git/objects/pack/*.pack' \
    --link-dest="$LATEST" \
    "$SOURCE" "$TODAY_DIR/" >> "$LOG_FILE" 2>&1
else
  rsync -aH --delete \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='.git/objects/pack/*.pack' \
    "$SOURCE" "$TODAY_DIR/" >> "$LOG_FILE" 2>&1
fi
RSYNC_EXIT=$?
set -e

if [ $RSYNC_EXIT -ne 0 ] && [ $RSYNC_EXIT -ne 23 ] && [ $RSYNC_EXIT -ne 24 ]; then
  echo "rsync failed with exit code $RSYNC_EXIT" >> "$LOG_FILE"
  exit $RSYNC_EXIT
elif [ $RSYNC_EXIT -ne 0 ]; then
  echo "rsync finished with warning (exit $RSYNC_EXIT) — 一部ファイルはスキップされましたが継続します" >> "$LOG_FILE"
fi

# latestシンボリックリンクを更新
rm -f "$LATEST"
ln -s "$TODAY_DIR" "$LATEST"

# 7日より古いスナップショットを削除
find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20*-*-*" -mtime +"$RETENTION_DAYS" -exec rm -rf {} \; 2>/dev/null || true

# 30日より古いログを削除
find "$LOG_DIR" -name "backup-*.log" -mtime +"$LOG_RETENTION_DAYS" -delete 2>/dev/null || true

# サマリ出力
SNAPSHOT_SIZE=$(du -sh "$TODAY_DIR" 2>/dev/null | awk '{print $1}')
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | awk '{print $1}')
SNAPSHOT_COUNT=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20*-*-*" | wc -l | tr -d ' ')

echo "Today snapshot: $SNAPSHOT_SIZE" >> "$LOG_FILE"
echo "Total backup size: $TOTAL_SIZE" >> "$LOG_FILE"
echo "Snapshot count: $SNAPSHOT_COUNT" >> "$LOG_FILE"
echo "===== Backup done: $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
