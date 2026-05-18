---
name: gmail-to-slack-notify
description: 【廃止済み】Gmail→Slack 通知。常駐bot (/Users/major/ai_work/main.py) に一本化済み。このSKILLを呼び出された場合は何もせず終了すること。
---

# このスキルは廃止されました（2026-05-19）

Gmail→Slack 通知は launchd 常駐の **Shota-Gmail-bot** (`/Users/major/ai_work/main.py`) に一本化されています。

## このスキルが呼ばれた場合の挙動

Claudeがこのスキルを呼び出された場合:
- **何もせず即時終了してください**。Slack へのメッセージ送信は禁止です。
- 二重送信防止のガードです。

## アクティブな仕組み（参考）

| 項目 | 内容 |
|------|------|
| 実行体 | `/Users/major/ai_work/main.py`（Python常駐） |
| launchd | `~/Library/LaunchAgents/io.wanderlust.gmail-bot.plist` |
| ポーリング | 60秒毎 |
| 通知形式 | 送信者 / 先方の会社 / 件名 / サマリ のみ（コンパクト） |
| チャンネル | `#z-shota-gmail` |
