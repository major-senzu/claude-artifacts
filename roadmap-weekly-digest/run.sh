#!/bin/bash
# 1,000億ロードマップ 週次ダイジェスト生成
# 毎週日曜 20:07 に launchd (com.ueyama.roadmap-weekly) から起動される。
# headless Claude が daily/ を集計 → weekly サマリ作成 → STATUS.md / dashboard.html 更新 → macOS通知。

set -u
WORKSPACE="/Users/major/Documents/00_Shota-all"
CLAUDE_BIN="/Users/major/.nvm/versions/node/v20.20.0/bin/claude"
LOG_DIR="/Users/major/Documents/claude-artifacts/roadmap-weekly-digest"
LOG="$LOG_DIR/last-run.log"

export PATH="/Users/major/.nvm/versions/node/v20.20.0/bin:/usr/local/bin:/usr/bin:/bin"

cd "$WORKSPACE" || exit 1

WEEK_ID=$(date +%G-W%V)

"$CLAUDE_BIN" -p "週次ダイジェストの自動実行です。.claude/skills/roadmap/SKILL.md の「週次ダイジェスト」手順に従って: (1) 10_ideas/1000億ロードマップ/daily/ の今週分を集計し、軸ごとの成果物数と進捗サマリ・TODOバーンダウン・来週のフォーカス提案1つを 10_ideas/1000億ロードマップ/daily/weekly-${WEEK_ID}.md に保存 (2) STATUS.md の直近の進捗と最終更新日を更新 (3) dashboard.html を最新データで再生成。今週dailyが空の場合は『今週は記録された成果物ゼロ』と正直に書く。" \
  --permission-mode bypassPermissions > "$LOG" 2>&1

STATUS=$?

if [ $STATUS -eq 0 ]; then
  osascript -e 'display notification "週次ダイジェストを生成しました。dashboard.html をチェック" with title "🎯 1,000億ロードマップ" sound name "Glass"'
else
  osascript -e 'display notification "週次ダイジェスト生成に失敗（last-run.log参照）" with title "🎯 1,000億ロードマップ"'
fi

exit $STATUS
