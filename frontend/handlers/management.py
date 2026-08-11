"""Read-only manager views for district, site, and ticket recaps."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from api_client import (
    BackendAPIError,
    get_management_details,
    get_management_recap,
    get_management_site_details,
    get_management_sites,
)


DISTRICT_MENU = [["More Info", "Site Info"], ["Active Tickets"]]
SITE_MENU = [["More Info", "District Info"], ["Active Tickets"]]
BACK_MENU = [["Back"]]


def _district_menu():
    return ReplyKeyboardMarkup(
        DISTRICT_MENU, resize_keyboard=True, one_time_keyboard=False, is_persistent=True,
    )


def _site_menu():
    return ReplyKeyboardMarkup(
        SITE_MENU, resize_keyboard=True, one_time_keyboard=False, is_persistent=True,
    )


def _back_menu():
    return ReplyKeyboardMarkup(
        BACK_MENU, resize_keyboard=True, one_time_keyboard=False, is_persistent=True,
    )


def _district(context):
    """Use the admin-selected district when the user is simulating a manager."""
    return context.user_data.get("admin_view_district")


def _summary_text(summary, label):
    return (
        f"{label}: {summary.get('district') or summary.get('site_id')}\n\n"
        f"Total Problems: {summary['count_problems']}\n"
        f"Solved RCA: {summary['solved_rca']}\n"
        f"Solved Service: {summary['solved_service']}\n"
        f"Average RCA Time: {summary.get('solved_rca_avg_time') or '-'} hari\n"
        f"Average Service Time: {summary.get('solved_service_avg_time') or '-'} hari"
    )


async def show_manager_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu 1: district-level overview, opened by /start."""
    try:
        summary = await get_management_recap(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"Error: {exc}")
        return

    context.user_data["manager_mode"] = True
    context.user_data["manager_screen"] = "district"
    context.user_data["manager_waiting_site"] = False
    context.user_data.pop("manager_current_site", None)
    await update.effective_message.reply_text(
        "DISTRICT RECAP\nDistrict-level overview\n\n"
        + _summary_text(summary, "District"),
        reply_markup=_district_menu(),
    )


async def show_manager_details(update, context):
    """Show each RCA-level tracking_detail record without re-aggregating it."""
    try:
        payload = await get_management_details(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"Error: {exc}")
        return

    lines = ["DISTRICT RECAP - MORE INFO", "RCA-level breakdown", ""]
    if not payload["details"]:
        lines.append("Tidak ada data RCA.")
    else:
        for detail in payload["details"]:
            lines.append(
                f"{detail['rca_name']}\n"
                f"Problems: {detail['count_problems']} | RCA solved: {detail['solved_rca']} | "
                f"Service solved: {detail['solved_service']}\n"
                f"Avg RCA: {detail.get('solved_rca_avg_time') or '-'} hari | "
                f"Avg Service: {detail.get('solved_service_avg_time') or '-'} hari"
            )
    context.user_data["manager_screen"] = "district_details"
    await update.effective_message.reply_text("\n\n".join(lines), reply_markup=_back_menu())


async def show_manager_sites(update, context):
    """Menu 2: all tracking_summary_site records for the current district."""
    try:
        payload = await get_management_sites(update.effective_user.id, _district(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"Error: {exc}")
        return

    sites = payload["sites"]
    context.user_data["manager_sites"] = sites
    context.user_data["manager_waiting_site"] = False
    context.user_data["manager_screen"] = "sites"

    lines = ["SITE RECAP", "Site-level overview", ""]
    if not sites:
        lines.append("Tidak ada data site.")
    else:
        for site in sites:
            lines.append(_summary_text(site, "Site"))
    await update.effective_message.reply_text("\n\n".join(lines), reply_markup=_site_menu())


async def prompt_for_site_details(update, context):
    """Ask for one site, retaining the current district's site list as context."""
    sites = context.user_data.get("manager_sites")
    if sites is None:
        try:
            payload = await get_management_sites(update.effective_user.id, _district(context))
        except BackendAPIError as exc:
            await update.effective_message.reply_text(f"Error: {exc}")
            return
        sites = payload["sites"]
        context.user_data["manager_sites"] = sites

    if not sites:
        await update.effective_message.reply_text("Tidak ada site untuk dipilih.", reply_markup=_site_menu())
        return

    choices = "\n".join(f"{number}. {site['site_id']}" for number, site in enumerate(sites, start=1))
    context.user_data["manager_waiting_site"] = True
    context.user_data["manager_screen"] = "site_picker"
    await update.effective_message.reply_text(
        "Pilih site untuk More Info dengan membalas nomornya:\n\n" + choices,
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_manager_site_details(update, context, site_id):
    """Show only tracking_detail_site entries for the chosen site."""
    try:
        payload = await get_management_site_details(
            update.effective_user.id, site_id, _district(context)
        )
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"Error: {exc}")
        return

    context.user_data["manager_current_site"] = site_id
    context.user_data["manager_waiting_site"] = False
    context.user_data["manager_screen"] = "site_details"
    lines = [f"SITE RECAP - MORE INFO\nSite: {site_id}", "RCA-level breakdown", ""]
    if not payload["details"]:
        lines.append("Tidak ada data RCA.")
    else:
        for detail in payload["details"]:
            lines.append(
                f"{detail['rca_name']}\n"
                f"Problems: {detail['count_problems']} | RCA solved: {detail['solved_rca']} | "
                f"Service solved: {detail['solved_service']}\n"
                f"Avg RCA: {detail.get('solved_rca_avg_time') or '-'} hari | "
                f"Avg Service: {detail.get('solved_service_avg_time') or '-'} hari"
            )
    await update.effective_message.reply_text("\n\n".join(lines), reply_markup=_back_menu())


async def show_manager_tickets(update, context):
    """Menu 3: engineer-like dashboard with all input disabled."""
    from handlers.ticket import show_ticket_dashboard

    await show_ticket_dashboard(update, context, interactive=False)
    context.user_data["manager_screen"] = "tickets"
    # A manager can always navigate back to the relevant recap from tickets.
    await update.effective_message.reply_text(
        "VIEW TICKETS\nRead-only ticket view.",
        reply_markup=ReplyKeyboardMarkup(
            [["District Info", "Site Info"]],
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True,
        ),
    )


async def process_manager_input(update, context):
    """Route only manager navigation; ticket and RCA input is never enabled here."""
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
        await show_manager_site_details(update, context, sites[number - 1]["site_id"])
        return

    screen = context.user_data.get("manager_screen", "district")
    if message == "More Info":
        if screen == "district":
            await show_manager_details(update, context)
        elif screen == "sites":
            await prompt_for_site_details(update, context)
        return
    if message == "Back":
        if screen == "district_details":
            await show_manager_dashboard(update, context)
        elif screen == "site_details":
            await show_manager_sites(update, context)
        return
    if message == "District Info":
        await show_manager_dashboard(update, context)
    elif message == "Site Info":
        await show_manager_sites(update, context)
    elif message == "Active Tickets":
        await show_manager_tickets(update, context)
