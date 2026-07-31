from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menu import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Selamat datang di Bot Monitoring RCA.\n\n"
        "Silakan pilih menu di bawah ini.",
        reply_markup=main_menu()
    )