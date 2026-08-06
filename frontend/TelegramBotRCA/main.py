from config import TOKEN, validate_config

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.start import start
from handlers.management import management, back_to_main
from handlers.engineer import engineer
from handlers.notification import notify_engineers

from handlers.ticket import (
    show_ticket_dashboard,
    process_text_input,
)


def main():
    validate_config()

    app = ApplicationBuilder().token(TOKEN).build()

    # ======================================
    # START
    # ======================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )
    app.add_handler(CommandHandler("notify_engineers", notify_engineers))

    # ======================================
    # MANAGEMENT
    # ======================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^👨‍💼 Management$"),
            management
        )
    )

    # ======================================
    # ENGINEER
    # ======================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^👷 Engineer Field"),
            engineer
        )
    )

    # ======================================
    # VIEW TICKET
    # ======================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^🎫 View Ticket$"),
            show_ticket_dashboard
        )
    )

    # ======================================
    # KEMBALI
    # ======================================

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^⬅️ Kembali$"),
            back_to_main
        )
    )

    # One text handler routes replies based on the user's current step.
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            process_text_input
        )
    )

    print("✅ Bot sedang berjalan...")

    app.run_polling()


if __name__ == "__main__":
    main()
