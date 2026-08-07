from telegram import ReplyKeyboardRemove

from api_client import BackendAPIError, get_tickets


def _ticket_label(ticket):
    identifiers = ticket["identifiers"]
    if ticket["ticket_type"] == "ZP":
        location = f"eNodeB {identifiers['enodeb_id']} / Cell {identifiers['cell_id']}"
    else:
        location = f"LAC {identifiers['lac']} / CI {identifiers['ci']}"
    return f"#{ticket['ticket_id']} ({ticket['ticket_type']}, {location})"


async def show_ticket_dashboard(update, context):
    try:
        telegram_id = update.effective_user.id
        payload = await get_tickets(telegram_id)
    except BackendAPIError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    context.user_data["ticket_list"] = []
    ticket_groups = payload["tickets"]
    need_servicing = ticket_groups["need_service"]
    need_analyzing = ticket_groups["need_analysis"]

    text = f"TICKET DASHBOARD — {payload['district']}\n\nNeed Servicing\n\n"
    if not need_servicing:
        text += "Tidak ada tiket.\n\n"
    else:
        for ticket in need_servicing:
            text += f"- {_ticket_label(ticket)}\n  Site: {ticket['site_id']}\n\n"

    text += "Need Analyzing\n\n"
    if not need_analyzing:
        text += "Tidak ada tiket."
    else:
        for number, ticket in enumerate(need_analyzing, start=1):
            text += f"{number}. {_ticket_label(ticket)}\n   Site: {ticket['site_id']} | Aging: {ticket['aging']} hari\n\n"
            context.user_data["ticket_list"].append(ticket)
        text += "Balas dengan nomor tiket yang ingin diproses."

    context.user_data["waiting_ticket"] = bool(need_analyzing)
    await update.message.reply_text(text)


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
    context.user_data["ticket"] = ticket
    context.user_data["waiting_ticket"] = False
    context.user_data["waiting_rca"] = True
    await update.message.reply_text(
        "DETAIL TIKET\n\n"
        f"Tiket: {_ticket_label(ticket)}\n"
        f"Site: {ticket['site_id']}\n"
        f"Aging: {ticket['aging']} hari\n\n"
        "Silakan masukkan nomor RCA.",
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
