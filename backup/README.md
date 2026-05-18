# 00_Shota-all 日次バックアップ

`00_Shota-all/` を毎日 03:00 に `~/Backups/00_Shota-all-backup/` へ自動バックアップする仕組み。

## 目的

- Claude Code が誤ってファイル削除・上書きした場合の保険
- 7世代（7日分）のスナップショットを保持、復元可能

## 仕組み

- `rsync --link-dest` によるハードリンク方式
- 変更のないファイルは前日のスナップショットへのリンク → 容量は増分のみ
- 例：100GBの00_Shota-allを7日保持しても、実使用は100GB + 差分のみ

## ファイル

| ファイル | 役割 |
|---------|------|
| `backup.sh` | バックアップ本体 |
| `com.ueyama.shota-all-backup.plist` | launchd 定期実行設定 |
| `install.sh` | 初回セットアップ |
| `uninstall.sh` | 解除 |

## セットアップ（初回のみ）

```bash
bash /Users/major/Documents/00_Shota-all/05_automation/backup/install.sh
```

## 手動実行

```bash
bash /Users/major/Documents/00_Shota-all/05_automation/backup/backup.sh
```

## 状況確認

```bash
# 実行履歴
launchctl list | grep shota-all-backup

# スナップショット一覧
ls -la ~/Backups/00_Shota-all-backup/

# 最新ログ
tail -50 ~/Backups/00_Shota-all-backup/_logs/backup-$(date +%Y-%m-%d).log
```

## 復元

最新のバックアップから復元：
```bash
# 例：特定ファイルを復元
cp ~/Backups/00_Shota-all-backup/latest/path/to/file /Users/major/Documents/00_Shota-all/path/to/file

# 例：フォルダ全体を復元
rsync -a ~/Backups/00_Shota-all-backup/latest/path/to/folder/ /Users/major/Documents/00_Shota-all/path/to/folder/
```

特定日付から復元：
```bash
ls ~/Backups/00_Shota-all-backup/  # 日付一覧を確認
cp ~/Backups/00_Shota-all-backup/2026-04-20/path/to/file ...
```

## 解除

```bash
bash /Users/major/Documents/00_Shota-all/05_automation/backup/uninstall.sh
```

## 注意

- `~/Backups/` は同じMac内なので、**SSD故障には対応できない**
- 物理故障対策は別途 Time Machine + 外付けSSD を推奨
- `.DS_Store` `node_modules` はバックアップ対象外
