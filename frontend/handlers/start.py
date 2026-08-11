from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from api_client import BackendAPIError, get_identity
from handlers.management import show_manager_dashboard
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
            "Admin mode. Pilih fitur yang ingin diuji:",
            reply_markup=ReplyKeyboardMarkup([["Manager"], ["Engineer"]], resize_keyboard=True),
        )
    elif identity["role"] == "manager":
        context.user_data["manager_mode"] = True
        await show_manager_dashboard(update, context)
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
        context.user_data["admin_setup_step"] = "district"
        await update.message.reply_text(
            "Masukkan district_operation_do:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if step == "district":
        district = message
        if not district:
            await update.message.reply_text("District tidak boleh kosong.")
            return
        context.user_data["admin_view_district"] = district
        context.user_data.pop("admin_setup_step", None)
        if context.user_data["admin_view_role"] == "manager":
            context.user_data["manager_mode"] = True
            context.user_data["ticket_view_district"] = district
            context.user_data["ticket_view_role"] = "manager"
            await show_manager_dashboard(update, context)
        else:
            context.user_data["ticket_view_district"] = district
            context.user_data["ticket_view_role"] = "engineer"
            await show_ticket_dashboard(update, context)
