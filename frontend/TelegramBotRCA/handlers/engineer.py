from telegram import ReplyKeyboardMarkup


async def engineer(update, context):
    """
    Menampilkan menu Engineer.
    """

    keyboard = [
        ["🎫 View Tickets"],
        ["⬅️ Kembali"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(
        "👷 *Menu Engineer Field*\n\n"
        "Silakan pilih menu di bawah ini.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )