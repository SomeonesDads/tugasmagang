from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from api_client import BackendAPIError, get_identity
from handlers.management import show_manager_dashboard
from handlers.master_management import show_master_dashboard
from handlers.ticket import show_ticket_dashboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route the user to the view appropriate for their assigned role."""
    try:
        identity = await get_identity(update.effective_user.id)
    except BackendAPIError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    context.user_data.clear()
    if identity["role"] == "admin":
        context.user_data["admin_setup_step"] = "role"
        await update.message.reply_text(
            "Admin mode. Simulasikan sebagai Manager atau Engineer:",
            reply_markup=ReplyKeyboardMarkup([["Manager"], ["Engineer"]], resize_keyboard=True),
        )
    elif identity["role"] == "manager":
        context.user_data["manager_mode"] = True
        await show_manager_dashboard(update, context)
    elif identity["role"] == "master_manager":
        await show_master_dashboard(update, context)
    else:
        await show_ticket_dashboard(update, context)


async def process_admin_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip() if update.message else ""
    step = context.user_data.get("admin_setup_step")
    if step == "role":
        normalized = message.lower()
        if normalized not in {"manager", "engineer"}:
            await update.message.reply_text("Pilih Manager atau Engineer.")
            return
        context.user_data["admin_view_role"] = normalized
        if normalized == "manager":
            # Admins use the global manager dashboard, so there is no NPO
            # scope to collect before showing it.
            context.user_data.pop("admin_setup_step", None)
            await show_master_dashboard(update, context)
            return
        context.user_data["admin_setup_step"] = "scope"
        await update.message.reply_text(
            "Masukkan departement_ns / NPO yang ingin digunakan:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if step == "scope":
        scope = message
        if not scope:
            await update.message.reply_text("NPO tidak boleh kosong.")
            return
        context.user_data["admin_view_district"] = scope
        context.user_data.pop("admin_setup_step", None)
        context.user_data["ticket_view_district"] = scope
        context.user_data["ticket_view_role"] = "engineer"
        await show_ticket_dashboard(update, context)
