# Claude Artifacts

Claude Code で作成した成果物の集約フォルダ。**公開系GitHub Pages 3本** ＋ **ローカル自動化スクリプト** を一箇所にまとめている。

## フォルダ構成

```
claude-artifacts/
├── shota-ueyama/             # パーソナルサイト本体（独立Gitリポ・Pages公開）
├── shota-portal/             # 公開github.ioリンク集ポータル（独立Gitリポ・Pages公開）
├── wl-private-artifacts/     # Wanderlust業務成果物（独立Gitリポ・Pages公開）
├── backup/                   # 00_Shota-all 日次バックアップ（launchd）
├── gmail-to-slack-notify/    # 【廃止済】旧Gmail→Slack通知スキル
└── website-image-check/      # パーソナルサイトの画像漏れチェッカー
```

## 各サブフォルダの役割

### 公開系（GitHub Pages）

| フォルダ | GitHub | Pages URL |
|---------|--------|-----------|
| `shota-ueyama` | https://github.com/major-senzu/shota-ueyama | https://major-senzu.github.io/shota-ueyama/ |
| `shota-portal` | https://github.com/major-senzu/shota-portal | https://major-senzu.github.io/shota-portal/ |
| `wl-private-artifacts` | https://github.com/major-senzu/wl-private-artifacts | https://major-senzu.github.io/wl-private-artifacts/ |
| （このリポ自身） | https://github.com/major-senzu/claude-artifacts | https://major-senzu.github.io/claude-artifacts/ |

### ローカル自動化系

| フォルダ | 用途 |
|---------|------|
| `backup` | 00_Shota-all を毎日03:00にバックアップ（launchd `com.ueyama.shota-all-backup`） |
| `gmail-to-slack-notify` | 【廃止済】旧Skill。常駐bot (`/Users/major/ai_work/`) に統合済み |
| `website-image-check` | パーソナルサイトの画像漏れ・URL切れチェッカー（Python CLI） |

## ソース・オブ・トゥルース

- **shota-ueyama** のソース: `00_Shota-all/01_personal/Shota's website/` → `deploy.sh` で同期 → push
- **wl-private-artifacts の組織図** のソース: `00_Shota-all/04_work/wanderlust/projects/<client>/組織図/`
- **backup** のターゲット: `00_Shota-all/` 全体 → `~/Backups/00_Shota-all-backup/`

## .gitignore の方針

公開系3サブリポは `.gitignore` で除外（各々独立リポなのでネスト管理しない）。ローカル自動化系は本リポにコミット。

## 関連: Shota-Gmail-bot

Gmail→Slack 通知の常駐bot本体は `/Users/major/ai_work/`。API鍵やGmail OAuth tokenを含むため、機密性確保のため claude-artifacts に移していない。launchd: `io.wanderlust.gmail-bot`。
