import os
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
IRAN = ZoneInfo("Asia/Tehran")

REPORT_HOURS = [10, 11, 12, 13, 14, 16]
sent_today = set()
chat_ids = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids.add(update.effective_chat.id)

    await update.message.reply_text(
        "سلام! ربات پایش بازار آهن فعال شد.\n\n"
        "گزارش‌ها در ساعت‌های ۱۰، ۱۱، ۱۲، ۱۳، ۱۴ و ۱۶ ارسال می‌شوند.\n"
        "فعلاً در مرحله راه‌اندازی هستیم و اتصال منابع قیمت "
        "هنوز انجام نشده است.\n\n"
        "دستورها:\n"
        "/status - وضعیت ربات\n"
        "/help - راهنما"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ربات اجرا شده است.\n"
        "منابع قیمت هنوز متصل نشده‌اند."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "دستورهای ربات:\n"
        "/start - شروع\n"
        "/status - وضعیت\n"
        "/help - راهنما"
    )


async def scheduled_reports(app: Application):
    while True:
        now = datetime.now(IRAN)
        key = (now.date(), now.hour)

        if (
            now.hour in REPORT_HOURS
            and now.minute == 0
            and key not in sent_today
        ):
            sent_today.add(key)

            message = (
                f"گزارش پایش بازار آهن\n"
                f"تاریخ: {now:%Y/%m/%d}\n"
                f"ساعت: {now:%H:%M}\n\n"
                "هنوز منبع قیمت به ربات متصل نشده است.\n"
                "پس از تکمیل اتصال منابع، قیمت‌ها و "
                "تغییرات بازار در این بخش نمایش داده می‌شوند."
            )

            for chat_id in list(chat_ids):
                try:
                    await app.bot.send_message(
                        chat_id=chat_id,
                        text=message
                    )
                except Exception as error:
                    print(f"خطا در ارسال گزارش: {error}")

        if now.hour == 0 and now.minute == 0:
            sent_today.clear()

        await asyncio.sleep(20)


async def post_init(app: Application):
    app.create_task(scheduled_reports(app))


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()


if __name__ == "__main__":
    main()
