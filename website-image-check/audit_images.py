#!/usr/bin/env python3
"""
website 画像監査スクリプト

リサーチページの index.html カードと、各詳細ページの hero-face 画像が
- ちゃんと <img> タグを持っているか
- URL が HTTP 200 を返すか
- index カードと詳細ページの画像 URL が一致しているか

をチェックする。

使い方:
  python3 audit_images.py [--dir <path>] [--no-network]

デフォルト対象: 01_personal/Shota's website/no2-legends/
他の研究ディレクトリ（geo-history 等）も --dir で指定可。

終了コード: 0=全OK / 1=要修正

Wikipedia の Special:FilePath/ リダイレクタ URL は HEAD で 302 を返すので
正常扱い。upload.wikimedia.org の直接 URL は 200 が期待値。
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, field

REPO_ROOT = Path("/Users/major/Documents/00_Shota-all")
DEFAULT_DIR = REPO_ROOT / "01_personal" / "Shota's website" / "no2-legends"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

OK_BADGE = f"{GREEN}✓{RESET}"
ERR_BADGE = f"{RED}✗{RESET}"
WARN_BADGE = f"{YELLOW}⚠{RESET}"

NAME_RE = re.compile(r'<div class="name">([^<]+)</div>')
IMG_IN_FACE_RE = re.compile(
    r'<div class="(?:hero-face|face)"[^>]*>\s*<img\s+src="([^"]+)"',
    re.DOTALL,
)
INITIALS_RE = re.compile(r'data-initials="([^"]+)"')
HERO_FACE_RE = re.compile(
    r'<div class="hero-face"[^>]*data-initials="(?P<initials>[^"]+)"[^>]*>(?P<inner>.*?)</div>',
    re.DOTALL,
)


@dataclass
class CardEntry:
    status: str  # done | todo | pending
    name: str
    initials: str | None
    href: str | None
    img_url: str | None


@dataclass
class DetailEntry:
    path: Path
    initials: str | None
    img_url: str | None


@dataclass
class Issue:
    severity: str  # error | warn
    where: str
    msg: str


def parse_index_cards(index_html: str) -> list[CardEntry]:
    """Index の各 card を抽出。<a href> でラップされていれば href も取れる。"""
    cards: list[CardEntry] = []

    # まず <a href> ラップ済み（done で詳細ページへリンクされているもの）を消費
    consumed_spans: list[tuple[int, int]] = []

    linked_re = re.compile(
        r'<a href="\./(?P<href>[^"]+\.html)"[^>]*>\s*<div class="card (?P<status>done|todo|pending)[^"]*">(?P<inner>.*?)</div>\s*</a>',
        re.DOTALL,
    )
    for m in linked_re.finditer(index_html):
        inner = m.group("inner")
        cards.append(_card_from_inner(
            status=m.group("status"),
            inner=inner,
            href=m.group("href"),
        ))
        consumed_spans.append(m.span())

    def is_consumed(start: int, end: int) -> bool:
        for s, e in consumed_spans:
            if s <= start and end <= e:
                return True
        return False

    # 残りの <div class="card ..."> 単体（リンクなし）
    plain_re = re.compile(
        r'<div class="card (?P<status>done|todo|pending)[^"]*">(?P<inner>.*?)(?=\s*<div class="card |\s*</div>\s*</section>)',
        re.DOTALL,
    )
    for m in plain_re.finditer(index_html):
        if is_consumed(m.start(), m.end()):
            continue
        cards.append(_card_from_inner(
            status=m.group("status"),
            inner=m.group("inner"),
            href=None,
        ))
    return cards


def _card_from_inner(status: str, inner: str, href: str | None) -> CardEntry:
    name_m = NAME_RE.search(inner)
    name = name_m.group(1).strip() if name_m else "<no name>"
    initials_m = INITIALS_RE.search(inner)
    initials = initials_m.group(1) if initials_m else None
    img_m = IMG_IN_FACE_RE.search(inner)
    img_url = img_m.group(1) if img_m else None
    return CardEntry(status=status, name=name, initials=initials, href=href, img_url=img_url)


def parse_detail_hero(detail_html: str) -> DetailEntry | None:
    m = HERO_FACE_RE.search(detail_html)
    if not m:
        return None
    inner = m.group("inner")
    img_m = re.search(r'<img\s+src="([^"]+)"', inner)
    img_url = img_m.group(1) if img_m else None
    return DetailEntry(path=Path(""), initials=m.group("initials"), img_url=img_url)


def head_check(url: str, timeout: float = 6.0) -> tuple[int, str]:
    """HEAD リクエスト。302 もOKとして扱う（Wikipedia FilePath が 302）。"""
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": "shota-website-image-audit/1.0 (local)",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, "OK"
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def status_badge(code: int) -> str:
    if 200 <= code < 400:
        return f"{GREEN}HTTP {code}{RESET}"
    if code == 0:
        return f"{RED}NETWORK FAIL{RESET}"
    return f"{RED}HTTP {code}{RESET}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="調査対象ディレクトリ（index.html を含む）")
    parser.add_argument("--no-network", action="store_true", help="HEAD リクエストをスキップ（ローカル整合性のみチェック）")
    args = parser.parse_args()

    target_dir = Path(args.dir).expanduser().resolve()
    index_path = target_dir / "index.html"

    if not index_path.exists():
        print(f"{ERR_BADGE} {index_path} が見つかりません", file=sys.stderr)
        return 1

    print(f"{BOLD}=== website 画像監査: {target_dir.relative_to(REPO_ROOT)} ==={RESET}\n")

    index_html = index_path.read_text(encoding="utf-8")
    cards = parse_index_cards(index_html)

    issues: list[Issue] = []

    # ───────────── INDEX セクション ─────────────
    print(f"{BOLD}[1] INDEX カード{RESET}  ({len(cards)} cards)")
    for card in cards:
        line_prefix = ""
        if card.status == "done":
            badge = OK_BADGE
        elif card.status == "todo":
            badge = WARN_BADGE if not card.img_url else OK_BADGE
        else:  # pending
            badge = DIM + "·" + RESET

        # done なのに href なし → リンク忘れ
        if card.status == "done" and not card.href:
            issues.append(Issue("error", f"index/{card.name}",
                                "DONE カードに <a href> 詳細ページリンクが無い"))
            badge = ERR_BADGE

        # done なのに img なし → 画像忘れ
        if card.status == "done" and not card.img_url:
            issues.append(Issue("error", f"index/{card.name}",
                                "DONE カードに <img> が無い (initials のみ)"))
            badge = ERR_BADGE

        # todo で img URL もない場合は warn（許容するが報告）
        if card.status == "todo" and not card.img_url:
            issues.append(Issue("warn", f"index/{card.name}",
                                "TODO カードに画像が未設定"))

        url_part = ""
        net_part = ""
        if card.img_url:
            url_part = f" {DIM}{_short(card.img_url)}{RESET}"
            if not args.no_network:
                code, msg = head_check(card.img_url)
                net_part = f"  {status_badge(code)}"
                if not (200 <= code < 400):
                    issues.append(Issue("error", f"index/{card.name}",
                                        f"画像 URL が壊れている ({code} {msg}): {card.img_url}"))
                    badge = ERR_BADGE

        href_part = f" {DIM}→ {card.href}{RESET}" if card.href else ""
        status_label = f"[{card.status.upper():>7}]"
        print(f"  {badge} {status_label} {card.name:<28}{href_part}{url_part}{net_part}")

    print()

    # ───────────── DETAIL ページ ─────────────
    detail_files = sorted(p for p in target_dir.glob("*.html") if p.name != "index.html")
    print(f"{BOLD}[2] 詳細ページの hero 画像{RESET}  ({len(detail_files)} pages)")

    # index 上の href → image URL の辞書（done のみ意味がある）
    index_by_href: dict[str, CardEntry] = {
        c.href: c for c in cards if c.href
    }

    for path in detail_files:
        html = path.read_text(encoding="utf-8")
        detail = parse_detail_hero(html)
        relname = path.name
        idx_card = index_by_href.get(relname)

        if detail is None:
            # hero-face div がそもそもない
            issues.append(Issue("error", f"detail/{relname}",
                                "<div class=\"hero-face\"> が見つからない"))
            print(f"  {ERR_BADGE} {relname:<32} hero-face セクションがない")
            continue

        if not detail.img_url:
            issues.append(Issue("error", f"detail/{relname}",
                                "hero に <img> が無い (initials のみ表示される)"))
            print(f"  {ERR_BADGE} {relname:<32} hero <img> 未設定 (initials='{detail.initials}')")
            continue

        # URL のネットワークチェック
        net_part = ""
        url_ok = True
        if not args.no_network:
            code, msg = head_check(detail.img_url)
            net_part = f"  {status_badge(code)}"
            if not (200 <= code < 400):
                url_ok = False
                issues.append(Issue("error", f"detail/{relname}",
                                    f"hero 画像 URL が壊れている ({code}): {detail.img_url}"))

        # index カードとの整合性: 同じ画像ファイル名（thumb サイズ違いはOK）か？
        consistency_msg = ""
        if idx_card and idx_card.img_url and detail.img_url:
            if not _same_image(idx_card.img_url, detail.img_url):
                issues.append(Issue("warn", f"detail/{relname}",
                                    "index カードの画像と詳細ページ hero の画像が別物"))
                consistency_msg = f"  {YELLOW}(index 画像と不一致){RESET}"

        badge = OK_BADGE if url_ok and not consistency_msg else (ERR_BADGE if not url_ok else WARN_BADGE)
        print(f"  {badge} {relname:<32} {DIM}{_short(detail.img_url)}{RESET}{net_part}{consistency_msg}")

    print()

    # ───────────── サマリ ─────────────
    errors = [i for i in issues if i.severity == "error"]
    warns = [i for i in issues if i.severity == "warn"]

    print(f"{BOLD}=== Summary ==={RESET}")
    print(f"  cards : {len(cards)} ({sum(1 for c in cards if c.status=='done')} done, "
          f"{sum(1 for c in cards if c.status=='todo')} todo, "
          f"{sum(1 for c in cards if c.status=='pending')} pending)")
    print(f"  detail: {len(detail_files)} files")
    print(f"  errors: {RED if errors else DIM}{len(errors)}{RESET}")
    print(f"  warns : {YELLOW if warns else DIM}{len(warns)}{RESET}")

    if errors:
        print(f"\n{BOLD}{RED}ERRORS:{RESET}")
        for i in errors:
            print(f"  {ERR_BADGE} {i.where}: {i.msg}")
    if warns:
        print(f"\n{BOLD}{YELLOW}WARNINGS:{RESET}")
        for i in warns:
            print(f"  {WARN_BADGE} {i.where}: {i.msg}")

    return 1 if errors else 0


def _short(url: str, n: int = 80) -> str:
    return url if len(url) <= n else url[:n - 1] + "…"


def _same_image(a: str, b: str) -> bool:
    """thumb のサイズ違いを同一視する。

    例: .../thumb/X/Y/Foo.jpg/250px-Foo.jpg と
        .../thumb/X/Y/Foo.jpg/400px-Foo.jpg は同じ画像。
    """
    def norm(u: str) -> str:
        u = re.sub(r"/\d+px-[^/]+$", "/", u)
        u = re.sub(r"\?width=\d+", "", u)
        return u.lower()
    return norm(a) == norm(b)


if __name__ == "__main__":
    sys.exit(main())
