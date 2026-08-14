"""「新規作成 → 修正」サイクルのモック検証（Claude・Telegram・git push は使わない）。

実行: python3 test_mock_cycle.py
"""
import os
import sys
import tempfile
from pathlib import Path

# テスト用フラグを import 前に設定する
os.environ["MOCK_MODE"] = "1"
os.environ["DRY_RUN"] = "1"
_tmp = tempfile.mkdtemp(prefix="mock-studio-test-")
os.environ["PAGES_DIR"] = str(Path(_tmp) / "pages")
os.environ["SESSION_FILE"] = str(Path(_tmp) / "sessions.json")

import config  # noqa: E402
import studio  # noqa: E402
from generator import MODE_APP, MODE_FIX, MODE_RESEARCH  # noqa: E402

CHAT_ID = "test-chat"
failures = []


def check(label, cond):
    print(("  OK  " if cond else "  NG  ") + label)
    if not cond:
        failures.append(label)


print("[1] 新規作成（アプリモック生成モード）")
r1 = studio.handle_instruction(CHAT_ID, "ポーカーのオッズ計算ができる簡易Webアプリのモックを作って")
check("モード判定 = app", r1["mode"] == MODE_APP)
p1 = config.PAGES_DIR / r1["filename"]
check("HTMLファイルが生成された", p1.exists())
check("URLが返却された", r1["url"].endswith(r1["filename"]))
check("セッションに直前ファイルが記録された",
      studio.sessions.get_last_file(CHAT_ID) == r1["filename"])

print("[2] 修正（既存ページの修正モード）")
r2 = studio.handle_instruction(CHAT_ID, "ボタンの色を青に修正して")
check("モード判定 = fix", r2["mode"] == MODE_FIX)
check("新規ファイルを作らず同一ファイルを更新した", r2["filename"] == r1["filename"])
check("修正内容がファイルに反映された",
      "FIXED: ボタンの色を青に修正して" in p1.read_text(encoding="utf-8"))

print("[3] 連続修正（セッション維持）")
r3 = studio.handle_instruction(CHAT_ID, "タイトルも変更して")
check("2回目の修正も同一ファイル", r3["filename"] == r1["filename"])

print("[4] 新規リサーチ（モード切替）")
r4 = studio.handle_instruction(CHAT_ID, "海外の最新LLM動向をリサーチしてまとめて")
check("モード判定 = research", r4["mode"] == MODE_RESEARCH)
check("新しいファイルが作られた", r4["filename"] != r1["filename"])
check("セッションが新ファイルに切り替わった",
      studio.sessions.get_last_file(CHAT_ID) == r4["filename"])

print("[5] リサーチ結果への修正（対象がスイッチする）")
r5 = studio.handle_instruction(CHAT_ID, "出典セクションを削除して")
check("修正対象が直前のリサーチファイル", r5["filename"] == r4["filename"])

print("[6] 明示プレフィックス")
check("classify /research", studio.classify("/research 円安の背景", "x.html") == MODE_RESEARCH)
check("classify /app", studio.classify("/app 家計簿を修正できるアプリ", "x.html") == MODE_APP)
check("classify /fix", studio.classify("/fix 背景を白に", "x.html") == MODE_FIX)

print("[7] 履歴なしチャットでは修正キーワードでも新規扱い")
r7 = studio.handle_instruction("new-chat", "タイマーを追加してアプリを作って")
check("履歴なし → fix ではない", r7["mode"] != MODE_FIX)

print()
if failures:
    print(f"FAILED: {len(failures)} 件 -> {failures}")
    sys.exit(1)
print("ALL TESTS PASSED")
