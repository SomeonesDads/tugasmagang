from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from api_client import (
    BackendAPIError,
    get_management_details,
    get_management_recap,
    get_management_site_details,
    get_management_site_recap,
    get_management_sites,
)


MANAGER_MENU = [
    ["📊 RCA Details", "🎫 Active Tickets"],
    ["📍 Sites"],
]


def _menu():
    return ReplyKeyboardMarkup(MANAGER_MENU, resize_keyboard=True)


def _district(context):
    return context.user_data.get("admin_view_district")


def _summary_text(summary, label="District"):
    return (
        f"{label}: {summary.get('district') or summary.get('site_id')}\n\n"
        f"Total Problems: {summary['count_problems']}\n"
        f"Solved RCA: {summary['solved_rca']}\n"
        f"Solved Service: {summary['solved_service']}\n"
        f"Average RCA Time: {summary.get('solved_rca_avg_time') or '-'} hari\n"
        f"Average Service Time: {summary.get('solved_service_avg_time') or '-'} hari"
    )


async def show_manager_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        summary = await get_management_recap(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    context.user_data["manager_mode"] = True
    context.user_data["manager_waiting_site"] = False
    await update.effective_message.reply_text(
        "MANAGEMENT RECAP\n\n" + _summary_text(summary),
        reply_markup=_menu(),
    )


async def show_manager_details(update, context):
    try:
        payload = await get_management_details(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    if not payload["details"]:
        text = "RCA DETAILS\n\nTidak ada data RCA."
    else:
        lines = ["RCA DETAILS", ""]
        for detail in payload["details"]:
            lines.append(
                f"- {detail['rca_name']}\n"
                f"  Problems: {detail['count_problems']} | RCA solved: {detail['solved_rca']} | "
                f"Service solved: {detail['solved_service']}\n"
                f"  Avg RCA: {detail.get('solved_rca_avg_time') or '-'} hari | "
                f"Avg Service: {detail.get('solved_service_avg_time') or '-'} hari"
            )
        text = "\n".join(lines)
    await update.effective_message.reply_text(text, reply_markup=_menu())


async def show_manager_sites(update, context):
    try:
        payload = await get_management_sites(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    sites = payload["sites"]
    context.user_data["manager_sites"] = sites
    context.user_data["manager_waiting_site"] = bool(sites)
    if not sites:
        await update.effective_message.reply_text("SITES\n\nTidak ada data site.", reply_markup=_menu())
        return

    lines = ["SITES", "", "Balas dengan nomor site untuk melihat detail:", ""]
    for number, site in enumerate(sites, start=1):
        lines.append(
            f"{number}. {site['site_id']} | Problems: {site['count_problems']} | "
            f"RCA: {site['solved_rca']} | Service: {site['solved_service']}"
        )
    await update.effective_message.reply_text("\n".join(lines), reply_markup=ReplyKeyboardRemove())


async def show_manager_site(update, context, site_id):
    try:
        summary = await get_management_site_recap(update.effective_user.id, site_id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    context.user_data["manager_current_site"] = site_id
    context.user_data["manager_waiting_site"] = False
    keyboard = [["📊 Site RCA Details"], ["⬅️ Sites"]]
    await update.effective_message.reply_text(
        f"SITE RECAP\n\n{_summary_text(summary, label='Site')}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def show_manager_site_details(update, context):
    site_id = context.user_data.get("manager_current_site")
    if not site_id:
        await show_manager_sites(update, context)
        return
    try:
        payload = await get_management_site_details(update.effective_user.id, site_id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    lines = [f"SITE RCA DETAILS — {site_id}", ""]
    if not payload["details"]:
        lines.append("Tidak ada data RCA.")
    else:
        for detail in payload["details"]:
            lines.append(
                f"- {detail['rca_name']}\n"
                f"  Problems: {detail['count_problems']} | RCA: {detail['solved_rca']} | "
                f"Service: {detail['solved_service']}"
            )
    await update.effective_message.reply_text("\n".join(lines), reply_markup=_menu())


async def process_manager_input(update, context):
    message = update.message.text.strip() if update.message else ""

    if context.user_data.get("manager_waiting_site"):
        if not message.isdigit():
            await update.message.reply_text("Masukkan nomor site.")
            return
        sites = context.user_data.get("manager_sites", [])
        number = int(message)
        if number < 1 or number > len(sites):
            await update.message.reply_text("Nomor site tidak ditemukan.")
            return
        await show_manager_site(update, context, sites[number - 1]["site_id"])
        return

    if message == "📊 RCA Details":
        await show_manager_details(update, context)
    elif message == "🎫 Active Tickets":
        from handlers.ticket import show_ticket_dashboard
        await show_ticket_dashboard(update, context, interactive=False)
        await update.effective_message.reply_text("Management menu:", reply_markup=_menu())
    elif message == "📍 Sites":
        await show_manager_sites(update, context)
    elif message == "📊 Site RCA Details":
        await show_manager_site_details(update, context)
    elif message == "⬅️ Sites":
        await show_manager_sites(update, context)
