"""Telegram ボット本体（long polling — サーバー公開・Webhook 不要）。

使い方:
    python3 bot.py
"""
import asyncio
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
import studio

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger("mock-studio")

MODE_LABELS = {
    "research": "リサーチレポート",
    "app": "アプリモック",
    "fix": "修正",
}

HELP_TEXT = (
    "使い方:\n"
    "・そのまま指示を送ると自動でモード判定します\n"
    "   例:「海外の最新LLM動向をリサーチしてまとめて」→ リサーチ\n"
    "   例:「ポーカーのオッズ計算アプリのモックを作って」→ アプリ生成\n"
    "   例:「ボタンを青にして」→ 直前ページの修正\n"
    "・明示指定: /research <テーマ> | /app <指示> | /fix <修正内容>\n"
    "・/status で直前の作業ファイルを確認"
)


def _authorized(update: Update) -> bool:
    chat_id = str(update.effective_chat.id)
    if chat_id not in config.ALLOWED_CHAT_IDS:
        logger.warning("Unauthorized chat: %s", chat_id)
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await update.message.reply_text(
            f"未許可のチャットです。chat_id: {update.effective_chat.id} を "
            "ALLOWED_CHAT_IDS に追加してください。"
        )
        return
    await update.message.reply_text("Mock Studio 起動中です。\n\n" + HELP_TEXT)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    last = studio.sessions.get_last_file(update.effective_chat.id)
    if last:
        await update.message.reply_text(
            f"直前の作業ファイル: {last}\n{config.BASE_URL}/{last}"
        )
    else:
        await update.message.reply_text("まだ作業履歴がありません。")


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        return
    chat_id = update.effective_chat.id
    text = update.message.text or ""
    if not text.strip():
        return

    await update.message.reply_text("受け付けました。作業中です…（数分かかります）")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    loop = asyncio.get_running_loop()
    try:
        # Claude CLI / git は同期処理なので executor に逃がす
        result = await loop.run_in_executor(
            None, studio.handle_instruction, chat_id, text
        )
    except Exception as e:  # ユーザーにはエラー内容を返して継続する
        logger.exception("handle_instruction failed")
        await update.message.reply_text(f"エラーが発生しました:\n{e}")
        return

    label = MODE_LABELS.get(result["mode"], result["mode"])
    await update.message.reply_text(
        f"完了しました（{label}）\n"
        f"{result['url']}\n\n"
        "※ GitHub Pages への反映に1〜2分かかる場合があります。\n"
        "続けて修正指示を送ると、このページを直接修正します。"
    )


def main() -> None:
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN が未設定です（.env を確認してください）")
    if not config.ALLOWED_CHAT_IDS:
        logger.warning(
            "ALLOWED_CHAT_IDS が空です。全メッセージを拒否します。"
            "まず /start を送って chat_id を確認し .env に設定してください。"
        )

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    # /fix /research /app は本文ごと on_message に渡す（classify がプレフィックスを解釈）
    app.add_handler(CommandHandler(["fix", "research", "app"], on_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logger.info("Mock Studio bot started (long polling)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
