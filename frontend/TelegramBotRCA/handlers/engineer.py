from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menu import engineer_menu


async def engineer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Menampilkan menu Engineer Field.
    """

    await update.message.reply_text(
        text=(
            "👷 Menu Engineer Field\n\n"
            "Silakan pilih menu di bawah ini."
        ),
        reply_markup=engineer_menu()
    )