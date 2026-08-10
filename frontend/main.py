from config import TOKEN, validate_config

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from handlers.notification import notify_engineers
from handlers.start import start
from handlers.ticket import process_text_input


def main():
    validate_config()

    app = ApplicationBuilder().token(TOKEN).build()

    # /start opens the current ticket dashboard directly.
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("notify_engineers", notify_engineers))

    # One text handler routes ticket number, RCA, and RCA-detail replies.
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_text_input)
    )

    print("âœ… Bot sedang berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
