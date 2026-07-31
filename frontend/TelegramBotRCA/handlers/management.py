from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menu import management_menu, main_menu


async def management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Menu Management\n\nSilakan pilih fitur yang ingin digunakan.",
        reply_markup=management_menu()
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kembali ke Menu Utama.",
        reply_markup=main_menu()
    )