# Mock Studio — スマホ指示型 Webリサーチ & アプリモック生成・修正システム

Telegram から指示を送ると、Claude Code がリサーチレポート／動作するアプリモックの
単一HTMLを生成・修正し、GitHub Pages に自動デプロイして URL を返信するボット。

## 機能モード

| モード | トリガー例 | 動作 |
|--------|-----------|------|
| ① リサーチ | 「海外の最新LLM動向をリサーチしてまとめて」 | Web検索 → 美麗レポートHTML生成 → デプロイ |
| ② アプリモック生成 | 「ポーカーのオッズ計算アプリのモックを作って」 | Tailwind/Lucide/Vanilla JS の動作する単一HTMLを生成 → デプロイ |
| ③ 既存ページ修正 | 「ボタンを青にして」「グラフを追加して」 | **直前に生成したファイル**を読み込んで修正 → 再デプロイ |

- モードはメッセージ内容から自動判定（修正キーワード＋直前ファイルあり → 修正、リサーチ系キーワード → リサーチ、それ以外 → アプリ生成）
- 明示指定も可能: `/research <テーマ>` `/app <指示>` `/fix <修正内容>`
- `/status` で直前の作業ファイルと URL を確認

## アーキテクチャ

```
スマホ (Telegram)
   │  long polling（Webhook不要・サーバー公開不要）
   ▼
bot.py ──── studio.py（モード判定・セッション管理）
              │
              ├─ generator.py … Claude Code CLI をヘッドレス実行
              │                  (claude -p "<プロンプト>" --permission-mode bypassPermissions)
              │                  → pages/<mode>-<timestamp>.html を生成/修正
              ├─ session.py  … sessions.json にチャットごとの直前ファイル名を保持
              └─ deployer.py … git add/commit/push（claude-artifacts リポ）
                                 → https://major-senzu.github.io/claude-artifacts/mock-studio/pages/<slug>.html
```

## セットアップ

### 1. 依存関係

```bash
cd /Users/major/Documents/claude-artifacts/mock-studio
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Telegram ボットの作成

1. Telegram で [@BotFather](https://t.me/BotFather) に `/newbot` を送りボットを作成
2. 発行されたトークンを控える

### 3. `.env` の設定

```bash
cp .env.example .env
```

| 変数 | 必須 | 説明 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | ✅ | BotFather で発行したトークン |
| `ALLOWED_CHAT_IDS` | ✅ | 応答を許可するチャットID（カンマ区切り）。**空だと全拒否**（安全側） |
| `CLAUDE_BIN` | — | Claude Code CLI のパス（デフォルト: `claude`） |
| `CLAUDE_TIMEOUT_SEC` | — | 生成タイムアウト秒（デフォルト: 1200） |
| `BASE_URL` | — | 公開URLのベース |
| `MOCK_MODE` / `DRY_RUN` | — | テスト用（Claude不使用 / push スキップ） |

自分の chat_id は、トークン設定後にボットへ `/start` を送ると「未許可のチャットです。chat_id: …」と表示されるので、それを `ALLOWED_CHAT_IDS` に設定して再起動する。

### 4. 起動

```bash
python3 bot.py
```

## テスト（モック実行）

Claude・Telegram・git push を一切使わずに「新規作成 → 修正 → モード切替」の
サイクルを検証する:

```bash
python3 test_mock_cycle.py
```

## セキュリティ上の注意

- `.env`（トークン）と `sessions.json` は `.gitignore` 済み。**コミットしない**
- `ALLOWED_CHAT_IDS` による許可制。未設定のまま公開ボットにしない
- `pages/` 配下は **公開リポジトリ経由で全世界に公開される**。機密情報・クライアント名を含む指示は送らない
