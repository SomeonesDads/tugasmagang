from datetime import datetime

from telegram import ReplyKeyboardRemove

from api_client import BackendAPIError, get_rca_options, get_tickets


def _ticket_label(ticket):
    identifiers = ticket["identifiers"]
    raw_date = ticket.get("created_date") or ticket.get("start_date")
    if raw_date:
        try:
            start_date = datetime.fromisoformat(str(raw_date)).strftime("%d/%m/%y")
        except ValueError:
            start_date = str(raw_date)
    else:
        start_date = "-"
    if ticket["ticket_type"] == "ZP":
        location = f"{ticket['site_id']}_{identifiers['enodeb_id']}_{identifiers['cell_id']}"
    else:
        location = f"{ticket['site_id']}_{identifiers['lac']}_{identifiers['ci']}"
    return f"#{ticket['ticket_id']} {ticket['ticket_type']} ({start_date})_{location}"


def _site_class(ticket):
    """Support both the grouped API response and older backend payloads."""
    return ticket.get("site_class", "-")


def _ticket_status(ticket):
    status = ticket.get("status", {})
    serviced = "✅" if status.get("serviced") else "❌"
    return f"Serviced: {serviced}"


async def show_ticket_dashboard(update, context):
    try:
        telegram_id = update.effective_user.id
        payload = await get_tickets(telegram_id)
    except BackendAPIError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    context.user_data["ticket_list"] = []
    ticket_groups = payload["tickets"]
    if isinstance(ticket_groups, list):
        # Older staging backends return a flat list with status metadata.
        need_servicing = [
            ticket for ticket in ticket_groups
            if ticket.get("status", {}).get("rca")
            and not ticket.get("status", {}).get("serviced")
        ]
        need_analyzing = [
            ticket for ticket in ticket_groups
            if not ticket.get("status", {}).get("rca")
        ]
    else:
        need_servicing = ticket_groups["need_service"]
        need_analyzing = ticket_groups["need_analysis"]

    text = (
        f"TICKET DASHBOARD — {payload['district']}\n\n"
        "Format: #ID TYPE (DD/MM/YY)_SITE_IDENTIFIER\n"
        "Serviced: ✅ sudah selesai | ❌ belum selesai\n\n"
        "Need Servicing\n\n"
    )
    if not need_servicing:
        text += "Tidak ada tiket.\n\n"
    else:
        for ticket in need_servicing:
            text += f"- {_ticket_label(ticket)}\n  Site: {ticket['site_id']} | Class: {_site_class(ticket)} | {_ticket_status(ticket)}\n\n"

    text += "Need Analyzing\n\n"
    if not need_analyzing:
        text += "Tidak ada tiket."
    else:
        for number, ticket in enumerate(need_analyzing, start=1):
            text += f"{number}. {_ticket_label(ticket)}\n   Site: {ticket['site_id']} | Class: {_site_class(ticket)} | {_ticket_status(ticket)} | Aging: {ticket['aging']} hari\n\n"
            context.user_data["ticket_list"].append(ticket)
        text += "Balas dengan nomor tiket yang ingin diproses."

    context.user_data["waiting_ticket"] = bool(need_analyzing)
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


async def select_ticket(update, context):
    if not update.message or not context.user_data.get("waiting_ticket"):
        return

    message = update.message.text.strip()
    if not message.isdigit():
        await update.message.reply_text("❌ Masukkan nomor tiket.")
        return

    number = int(message)
    ticket_list = context.user_data.get("ticket_list", [])
    if number < 1 or number > len(ticket_list):
        await update.message.reply_text("❌ Nomor tiket tidak ditemukan.")
        return

    ticket = ticket_list[number - 1]
    try:
        options = await get_rca_options()
    except BackendAPIError as exc:
        await update.message.reply_text(f"RCA options unavailable: {exc}")
        return

    categories = list(options)
    if not categories:
        await update.message.reply_text("Tidak ada pilihan RCA yang tersedia.")
        return

    context.user_data["ticket"] = ticket
    context.user_data["rca_options"] = options
    context.user_data["waiting_ticket"] = False
    context.user_data["waiting_rca"] = True
    rca_text = "\n".join(
        f"{index}. {category}" for index, category in enumerate(categories, start=1)
    )
    await update.message.reply_text(
        "DETAIL TIKET\n\n"
        f"Tiket: {_ticket_label(ticket)}\n"
        f"Site: {ticket['site_id']} | Class: {_site_class(ticket)}\n"
        f"{_ticket_status(ticket)}\n"
        f"Aging: {ticket['aging']} hari\n\n"
        "Pilih RCA:\n\n"
        f"{rca_text}\n\n"
        "Balas dengan nomor RCA.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def process_text_input(update, context):
    """Route a text reply to the current ticket/RCA step.

    python-telegram-bot executes only the first matching handler in a group,
    so this single router is required instead of three overlapping TEXT
    handlers.
    """
    if context.user_data.get("waiting_ticket"):
        await select_ticket(update, context)
    elif context.user_data.get("waiting_rca"):
        from handlers.rca import input_rca
        await input_rca(update, context)
    elif context.user_data.get("waiting_detail"):
        from handlers.rca import input_rca_detail
        await input_rca_detail(update, context)
