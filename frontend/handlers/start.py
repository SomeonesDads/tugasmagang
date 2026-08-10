from telegram import Update
from telegram.ext import ContextTypes

from handlers.ticket import show_ticket_dashboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start directly on the current ticket dashboard."""
    await show_ticket_dashboard(update, context)
