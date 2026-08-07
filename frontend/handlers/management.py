from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menu import main_menu, management_menu


async def management(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Menu Management\n\nSilakan pilih menu di bawah ini.",
        reply_markup=management_menu()
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message:

        await update.message.reply_text(
            "Kembali ke Menu Utama.",
            reply_markup=main_menu()
        )

    elif update.callback_query:

        query = update.callback_query

        await query.answer()

        await query.message.reply_text(
            "Kembali ke Menu Utama.",
            reply_markup=main_menu()
        )