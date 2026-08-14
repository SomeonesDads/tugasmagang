from datetime import time
from zoneinfo import ZoneInfo

from config import DAILY_BROADCAST_TIME, DAILY_BROADCAST_TIMEZONE, TOKEN, validate_config

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from handlers.notification import notify_engineers, scheduled_notify_engineers
from handlers.start import start
from handlers.ticket import paginate_ticket_dashboard, process_text_input
from handlers.history import paginate_history


def main():
    validate_config()

    app = ApplicationBuilder().token(TOKEN).build()

    # /start opens the dashboard appropriate to the Telegram user's role.
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("notify_engineers", notify_engineers))
    app.add_handler(CallbackQueryHandler(paginate_ticket_dashboard, pattern=r"^ticket_page:"))
    app.add_handler(CallbackQueryHandler(paginate_history, pattern=r"^history_page:"))

    # One text handler routes ticket number, RCA, and RCA-detail replies.
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_text_input)
    )

    try:
        hour, minute = (int(value) for value in DAILY_BROADCAST_TIME.split(":", 1))
        broadcast_time = time(hour=hour, minute=minute, tzinfo=ZoneInfo(DAILY_BROADCAST_TIMEZONE))
    except (ValueError, KeyError) as exc:
        raise RuntimeError(
            "DAILY_BROADCAST_TIME must be HH:MM and DAILY_BROADCAST_TIMEZONE must be valid"
        ) from exc
    if app.job_queue is None:
        raise RuntimeError("Install python-telegram-bot[job-queue] to enable daily broadcasts.")
    app.job_queue.run_daily(
        scheduled_notify_engineers,
        time=broadcast_time,
        name="daily-engineer-ticket-broadcast",
    )

    print("âœ… Bot sedang berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
