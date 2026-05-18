# Claude Artifacts

Claude Code で作成した成果物の集約フォルダ。配下に独立したGitHubリポジトリを並べて管理する。

## フォルダ構成

```
claude-artifacts/
├── shota-ueyama/          # 翔太のパーソナルサイト本体（独立リポ）
├── shota-portal/          # 公開済みgithub.io リンク集ポータル（独立リポ）
├── wl-private-artifacts/  # Wanderlust業務成果物（組織図・課題マップ等）（独立リポ）
└── （今後の新規システム）  # Claude Codeで作るシステムはここに新規ディレクトリで追加
```

## 各サブフォルダの役割

| フォルダ | GitHub | Pages URL |
|---------|--------|-----------|
| `shota-ueyama` | https://github.com/major-senzu/shota-ueyama | https://major-senzu.github.io/shota-ueyama/ |
| `shota-portal` | https://github.com/major-senzu/shota-portal | https://major-senzu.github.io/shota-portal/ |
| `wl-private-artifacts` | https://github.com/major-senzu/wl-private-artifacts | https://major-senzu.github.io/wl-private-artifacts/ |
| （このリポ自身） | https://github.com/major-senzu/claude-artifacts | https://major-senzu.github.io/claude-artifacts/ |

## ソース・オブ・トゥルース

- **shota-ueyama（パーソナルサイト）** のソースは `00_Shota-all/01_personal/Shota's website/`。`deploy.sh` で `claude-artifacts/shota-ueyama/` に同期 → push。
- **wl-private-artifacts の組織図** のソースは `00_Shota-all/04_work/wanderlust/projects/<client>/組織図/`。更新後 `claude-artifacts/wl-private-artifacts/<client>/org-chart.html` にコピー → push。
- **shota-portal** は単独管理。新サイト公開時にカードを追加。

## 注意

- 配下の3つのサブフォルダは `.gitignore` で除外しているため、このリポ（claude-artifacts）自体にはコミットされない。
- 各サブフォルダは独立したGitリポジトリ。それぞれの中で `git push` するとそれぞれのGitHubリポにpushされる。
