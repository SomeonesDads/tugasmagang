from config import TOKEN

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from handlers.start import start
from handlers.management import management, back_to_main
from handlers.engineer import engineer
from handlers.ticket import (
    view_tickets,
    select_ticket,
)

from handlers.rca import (
    select_rca,
    select_rca_detail,
)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # Handler /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^👨‍💼 Management$"),
            management
        )
    )

    app.add_handler(
    MessageHandler(
        filters.Regex(r"^👷 Engineer Field$"),
        engineer
        )
    )

    app.add_handler(
    MessageHandler(
        filters.Regex(r"^🎫 View Tickets$"),
        view_tickets
        )
    )

    app.add_handler(
    CallbackQueryHandler(
        select_ticket,
        pattern=r"^ticket_.*$"
        )
    )

    app.add_handler(
    CallbackQueryHandler(
        select_rca,
        pattern=r"^rca_.*$"
        )
    )

    app.add_handler(
    CallbackQueryHandler(
        select_rca_detail,
        pattern=r"^detail_.*$"
        )
    )

    app.add_handler(
    MessageHandler(
        filters.Regex(r"^⬅️ Kembali$"),
        back_to_main
        )
    )

    print("Bot sedang berjalan...")

    app.run_polling()


if __name__ == "__main__":
    main()