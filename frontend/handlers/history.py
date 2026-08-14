"""Read-only ticket history flow for engineers and managers."""

from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from api_client import BackendAPIError, get_ticket_history, get_ticket_history_detail


STATUS_LABELS = {"all": "All", "resolved": "Resolved", "need_analysis": "Need RCA", "need_service": "Need Service"}


def _filters_keyboard():
    return ReplyKeyboardMarkup(
        [["All", "Resolved"], ["Need RCA", "Need Service"], ["Site Filter", "Type Filter"], ["Date Filter", "RCA Filter"], ["Back"]],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def _history_args(context):
    state = context.user_data.get("history_filters", {})
    return {
        "status": state.get("status", "all"),
        "district_id": context.user_data.get("ticket_view_district"),
        "as_role": context.user_data.get("ticket_view_role"),
        "site_id": state.get("site_id"),
        "ticket_type": state.get("ticket_type"),
        "rca_id": state.get("rca_id"),
        "created_from": state.get("created_from"),
        "created_to": state.get("created_to"),
        "page": state.get("page", 1),
        "page_size": 10,
        "sort": "created_date",
        "order": "desc",
    }


def _identifier_text(ticket):
    ids = ticket.get("identifiers", {})
    if ticket.get("ticket_type") == "ZP":
        return f"eNodeB {ids.get('enodeb_id', '-')} / Cell {ids.get('cell_id', '-')}"
    return f"LAC {ids.get('lac', '-')} / CI {ids.get('ci', '-')}"


async def show_history_filters(update: Update, context, reset=False):
    if reset or "history_filters" not in context.user_data:
        context.user_data["history_filters"] = {"status": "all", "page": 1}
    context.user_data["history_screen"] = "filters"
    context.user_data["history_waiting"] = None
    await update.effective_message.reply_text(
        "TICKET HISTORY\nPilih status atau filter tambahan.",
        reply_markup=_filters_keyboard(),
    )


async def show_history_page(update, context, page=None):
    state = context.user_data.setdefault("history_filters", {"status": "all", "page": 1})
    if page is not None:
        state["page"] = page
    try:
        payload = await get_ticket_history(update.effective_user.id, **_history_args(context))
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}", reply_markup=_filters_keyboard())
        return
    tickets = payload.get("tickets", [])
    context.user_data["history_tickets"] = tickets
    context.user_data["history_screen"] = "list"
    lines = [f"TICKET HISTORY — {payload.get('district', '-')}", f"Filter: {STATUS_LABELS.get(state.get('status'), 'All')}", ""]
    if not tickets:
        lines.append("Tidak ada tiket pada filter ini.")
    for ticket in tickets:
        status = ticket.get("status", {})
        rca = "✅" if status.get("rca_submitted") else "❌"
        service = "✅" if status.get("service_closed") else "❌"
        lines.append(
            f"#{ticket['ticket_id']} {ticket['ticket_type']} | {ticket['created_date']} | {ticket['site_id']}\n"
            f"{_identifier_text(ticket)} | RCA {rca} | Service {service}"
        )
    lines.append(f"\nHalaman {payload['page']}/{payload['total_pages']}. Balas dengan ticket ID untuk detail.")
    navigation = []
    if payload["page"] > 1:
        navigation.append(InlineKeyboardButton("Previous", callback_data=f"history_page:{payload['page'] - 1}"))
    if payload["page"] < payload["total_pages"]:
        navigation.append(InlineKeyboardButton("Next", callback_data=f"history_page:{payload['page'] + 1}"))
    await update.effective_message.reply_text(
        "\n\n".join(lines),
        reply_markup=InlineKeyboardMarkup([navigation]) if navigation else _filters_keyboard(),
    )


async def show_history_detail(update, context, ticket_id):
    try:
        ticket = await get_ticket_history_detail(
            update.effective_user.id,
            ticket_id,
            district_id=context.user_data.get("ticket_view_district"),
            as_role=context.user_data.get("ticket_view_role"),
        )
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return
    status = ticket["status"]
    rca = ticket.get("rca", {})
    service = ticket.get("service", {})
    metrics = ticket.get("metrics", {})
    text = (
        f"TICKET DETAIL #{ticket['ticket_id']}\n\n"
        f"Type: {ticket['ticket_type']} | Site: {ticket['site_id']} | District: {ticket.get('district', '-')}\n"
        f"Created: {ticket['created_date']} | Aging: {ticket['aging']} hari\n"
        f"Identifiers: {_identifier_text(ticket)}\n\n"
        f"RCA: {rca.get('category') or '-'} / {rca.get('detail') or '-'}\n"
        f"Submitted: {rca.get('submitted_at') or '-'}\n"
        f"Service: {service.get('start_day') or '-'} → {service.get('end_day') or '-'}\n"
        f"RCA duration: {metrics.get('rca_resolution_days') if metrics.get('rca_resolution_days') is not None else '-'} hari\n"
        f"Service duration: {metrics.get('service_resolution_days') if metrics.get('service_resolution_days') is not None else '-'} hari\n\n"
        f"Final status: {STATUS_LABELS.get(status['code'], status['code'])}\n\n"
        "Read-only history."
    )
    context.user_data["history_screen"] = "detail"
    await update.effective_message.reply_text(text, reply_markup=_filters_keyboard())


async def process_history_input(update, context):
    message = update.message.text.strip() if update.message else ""
    state = context.user_data.setdefault("history_filters", {"status": "all", "page": 1})
    waiting = context.user_data.get("history_waiting")
    if waiting:
        context.user_data["history_waiting"] = None
        if waiting == "site":
            if not message:
                await update.message.reply_text("Site ID tidak boleh kosong.")
                return
            state["site_id"] = message
        elif waiting == "type":
            value = message.upper()
            if value not in {"ZP", "ZT"}:
                await update.message.reply_text("Ticket type harus ZP atau ZT.")
                return
            state["ticket_type"] = value
        elif waiting == "date":
            parts = [part.strip() for part in message.split(",")]
            if len(parts) != 2:
                await update.message.reply_text("Kirim tanggal sebagai YYYY-MM-DD,YYYY-MM-DD.")
                return
            try:
                start, end = (date.fromisoformat(part) for part in parts)
            except ValueError:
                await update.message.reply_text("Tanggal tidak valid. Gunakan format YYYY-MM-DD.")
                return
            if start > end:
                await update.message.reply_text("Tanggal awal tidak boleh setelah tanggal akhir.")
                return
            state["created_from"], state["created_to"] = parts
        elif waiting == "rca":
            if not message.isdigit() or int(message) < 1:
                await update.message.reply_text("RCA category harus berupa ID angka positif.")
                return
            state["rca_id"] = int(message)
        state["page"] = 1
        await show_history_page(update, context)
        return
    status = {label: code for code, label in STATUS_LABELS.items()}
    if message in status:
        state["status"] = status[message]
        state["page"] = 1
        await show_history_page(update, context)
    elif message == "Site Filter":
        context.user_data["history_waiting"] = "site"
        await update.message.reply_text("Masukkan Site ID:", reply_markup=ReplyKeyboardRemove())
    elif message == "Type Filter":
        context.user_data["history_waiting"] = "type"
        await update.message.reply_text("Masukkan ticket type (ZP atau ZT):", reply_markup=ReplyKeyboardRemove())
    elif message == "Date Filter":
        context.user_data["history_waiting"] = "date"
        await update.message.reply_text("Masukkan rentang tanggal: YYYY-MM-DD,YYYY-MM-DD", reply_markup=ReplyKeyboardRemove())
    elif message == "RCA Filter":
        context.user_data["history_waiting"] = "rca"
        await update.message.reply_text("Masukkan RCA category ID:", reply_markup=ReplyKeyboardRemove())
    elif message == "Back":
        context.user_data.pop("history_screen", None)
        context.user_data.pop("history_waiting", None)
        if context.user_data.get("manager_mode"):
            from handlers.management import show_manager_dashboard
            await show_manager_dashboard(update, context)
        else:
            from handlers.ticket import show_ticket_dashboard
            await show_ticket_dashboard(update, context, interactive=True)
    elif message.isdigit():
        ticket_id = int(message)
        visible_ids = {ticket.get("ticket_id") for ticket in context.user_data.get("history_tickets", [])}
        if context.user_data.get("history_screen") == "list" and ticket_id not in visible_ids:
            await update.message.reply_text("Ticket ID tidak ada di halaman yang sedang ditampilkan.")
            return
        await show_history_detail(update, context, ticket_id)
    else:
        await update.message.reply_text("Pilih filter yang tersedia atau kirim ticket ID.", reply_markup=_filters_keyboard())


async def paginate_history(update, context):
    query = update.callback_query
    await query.answer()
    try:
        page = int(query.data.split(":", 1)[1])
    except (AttributeError, IndexError, ValueError):
        return
    await show_history_page(update, context, page)
