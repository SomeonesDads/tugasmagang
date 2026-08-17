from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from api_client import BackendAPIError, get_rca_options, get_tickets


TELEGRAM_MESSAGE_LIMIT = 4096
TICKETS_PER_PAGE = 10


async def _reply_long_message(message, text, **kwargs):
    """Send text in Telegram-safe chunks while preserving markup on the last one."""
    lines = text.splitlines(keepends=True)
    chunks = []
    current = ""

    for line in lines:
        if len(line) > TELEGRAM_MESSAGE_LIMIT:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(
                line[index:index + TELEGRAM_MESSAGE_LIMIT]
                for index in range(0, len(line), TELEGRAM_MESSAGE_LIMIT)
            )
        elif len(current) + len(line) > TELEGRAM_MESSAGE_LIMIT:
            chunks.append(current)
            current = line
        else:
            current += line

    if current or not chunks:
        chunks.append(current)

    for index, chunk in enumerate(chunks):
        reply_kwargs = kwargs if index == len(chunks) - 1 else {}
        await message.reply_text(chunk, **reply_kwargs)


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


async def show_ticket_dashboard(update, context, interactive=True, page=0):
    message = update.effective_message
    try:
        telegram_id = update.effective_user.id
        payload = await get_tickets(
            telegram_id,
            district_id=context.user_data.get("ticket_view_district"),
            as_role=context.user_data.get("ticket_view_role"),
            page=page + 1,
            page_size=TICKETS_PER_PAGE,
        )
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
        "Format:\n#ID ZP (DD/MM/YY)_SITE_EnodeBID_Cell\natau\n#ID ZT (DD/MM/YY)_SITE_Lac_Ci\n"
        "============================================\n"
        "Need Servicing\n\n"
    )
    if not need_servicing:
        text += "Tidak ada tiket.\n\n"
    else:
        for ticket in need_servicing:
            text += f"- {_ticket_label(ticket)}\nAging: {ticket['aging']} hari | Class: {_site_class(ticket)}\n\n"

    text += "Need Analyzing\n\n"
    page_count = payload.get("total_pages", 1)
    page = max(0, min(page, page_count - 1))
    page_tickets = need_analyzing
    if not need_analyzing:
        text += "Tidak ada tiket."
    else:
        for number, ticket in enumerate(page_tickets, start=1):
            text += f"{number}. {_ticket_label(ticket)}\nAging: {ticket['aging']} hari | Class: {_site_class(ticket)} | {_ticket_status(ticket)} \n\n"
        if interactive:
            text += f"Halaman {page + 1}/{page_count}. Balas dengan nomor tiket pada halaman ini."

    context.user_data["waiting_ticket"] = interactive and bool(need_analyzing)
    context.user_data["ticket_list"] = page_tickets
    keyboard = []
    context.user_data["ticket_dashboard_interactive"] = interactive
    if page_count > 1:
        navigation = []
        if page > 0:
            navigation.append(InlineKeyboardButton("Sebelumnya", callback_data=f"ticket_page:{page - 1}"))
        if page < page_count - 1:
            navigation.append(InlineKeyboardButton("Berikutnya", callback_data=f"ticket_page:{page + 1}"))
        keyboard.append(navigation)
    await _reply_long_message(
        message,
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else ReplyKeyboardRemove(),
    )


async def paginate_ticket_dashboard(update, context):
    query = update.callback_query
    await query.answer()
    try:
        page = int(query.data.split(":", 1)[1])
    except (AttributeError, IndexError, ValueError):
        return
    await show_ticket_dashboard(
        update,
        context,
        interactive=context.user_data.get("ticket_dashboard_interactive", True),
        page=page,
    )


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
    if update.message and update.message.text.strip() == "Ticket History" and not context.user_data.get("manager_mode"):
        context.user_data["ticket_view_role"] = "engineer"
        from handlers.history import show_history_filters
        await show_history_filters(update, context, reset=True)
    elif context.user_data.get("admin_setup_step"):
        from handlers.start import process_admin_setup
        await process_admin_setup(update, context)
    elif context.user_data.get("history_screen") or context.user_data.get("history_waiting"):
        from handlers.history import process_history_input
        await process_history_input(update, context)
    elif context.user_data.get("manager_mode"):
        from handlers.management import process_manager_input
        await process_manager_input(update, context)
    elif context.user_data.get("master_mode"):
        from handlers.master_management import process_master_input
        await process_master_input(update, context)
    elif context.user_data.get("waiting_ticket"):
        await select_ticket(update, context)
    elif context.user_data.get("waiting_rca"):
        from handlers.rca import input_rca
        await input_rca(update, context)
    elif context.user_data.get("waiting_detail"):
        from handlers.rca import input_rca_detail
        await input_rca_detail(update, context)
