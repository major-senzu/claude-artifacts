# website-image-check

リサーチページ（no2-legends, geo-history など）の **画像漏れ・URL切れ** を自動検出するスクリプト。

リサーチページを作るたびに「index カード」と「詳細ページの hero」の両方に画像を入れる必要があるが、片方だけ忘れるケースが多い。これを毎回チェックする。

## 使い方

```bash
# デフォルト: no2-legends を監査
python3 /Users/major/Documents/00_Shota-all/05_automation/website-image-check/audit_images.py

# 別ディレクトリ（例: geo-history）
python3 .../audit_images.py --dir "/Users/major/Documents/00_Shota-all/01_personal/Shota's website/geo-history"

# ネットワーク不要（ローカルの構造整合性のみ）
python3 .../audit_images.py --no-network
```

## チェック項目

| # | チェック | 重要度 |
|---|---------|--------|
| 1 | `index.html` の DONE カードに `<a href>` リンクがあるか | error |
| 2 | DONE カードに `<img>` が入っているか（`data-initials` のみは NG） | error |
| 3 | カード画像 URL が HTTP 200 を返すか | error |
| 4 | 詳細ページに `<div class="hero-face">` があるか | error |
| 5 | 詳細ページの hero に `<img>` が入っているか | **error**（今回の漏れ） |
| 6 | hero 画像 URL が HTTP 200 を返すか | error |
| 7 | index カード画像と詳細ページ hero 画像が**同じ画像**か（thumb サイズ違いは許容） | warn |
| 8 | TODO カードに画像があるか | warn |

## 終了コード

- `0`: error なし（warn のみ／全 OK）
- `1`: error あり

## いつ実行すべきか

- リサーチページを新規作成した直後（必須）
- index.html を更新した直後
- deploy.sh で GitHub Pages に上げる前
- 月1回くらい全体の定期チェック

deploy.sh に組み込むことも可能（exit code 1 で失敗にする）。
