"""Daily real-ticket broadcasts to engineers."""

from telegram.error import TelegramError

from api_client import BackendAPIError, get_engineers, get_tickets


def _ticket_line(ticket):
    identifiers = ticket["identifiers"]
    if ticket["ticket_type"] == "ZP":
        identity = f"eNodeB {identifiers['enodeb_id']}/Cell {identifiers['cell_id']}"
    else:
        identity = f"LAC {identifiers['lac']}/CI {identifiers['ci']}"
    status = ticket.get("status", {})
    state = "Need Service" if status.get("rca") else "Need RCA"
    return (
        f"• #{ticket['ticket_id']} — {ticket['site_id']} ({identity}) | "
        f"{state} | aging {ticket['aging']} hari"
    )


async def _get_all_tickets(telegram_id):
    """Fetch every current ticket page for one engineer."""
    page = 1
    all_groups = {"need_service": [], "need_analysis": []}
    while True:
        payload = await get_tickets(
            telegram_id,
            as_role="engineer",
            page=page,
            page_size=50,
        )
        groups = payload.get("tickets", {})
        if isinstance(groups, list):
            groups = {
                "need_service": [
                    ticket for ticket in groups
                    if ticket.get("status", {}).get("rca")
                    and not ticket.get("status", {}).get("serviced")
                ],
                "need_analysis": [
                    ticket for ticket in groups
                    if not ticket.get("status", {}).get("rca")
                ],
            }
        for key in all_groups:
            all_groups[key].extend(groups.get(key, []))
        if page >= payload.get("total_pages", 1):
            return payload.get("district", "-"), all_groups
        page += 1


def _split_message(text, limit=4000):
    lines = text.splitlines(keepends=True)
    chunks = []
    current = ""
    for line in lines:
        if current and len(current) + len(line) > limit:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return chunks or [""]


async def broadcast_engineers(bot):
    """Broadcast each engineer their current district queue."""
    try:
        engineers = (await get_engineers())["engineers"]
    except BackendAPIError as exc:
        return [f"directory: gagal mengambil engineer ({exc})"]

    results = []
    for engineer in engineers:
        telegram_id = engineer["telegram_id"]
        try:
            district, groups = await _get_all_tickets(telegram_id)
            tickets = groups["need_service"] + groups["need_analysis"]
            lines = [
                "📋 DAILY TICKET BLAST",
                "",
                f"District: {district}",
                f"Total active tickets: {len(tickets)}",
                f"Need RCA: {len(groups['need_analysis'])}",
                f"Need Service: {len(groups['need_service'])}",
                "",
            ]
            lines.extend(_ticket_line(ticket) for ticket in tickets)
            lines.append("\nOpen the bot and choose View Ticket to process RCA.")
            for chunk in _split_message("\n".join(lines)):
                await bot.send_message(chat_id=telegram_id, text=chunk)
            results.append(f"{telegram_id}: terkirim ({len(tickets)} tiket)")
        except BackendAPIError as exc:
            results.append(f"{telegram_id}: gagal mengambil tiket ({exc})")
        except TelegramError as exc:
            results.append(f"{telegram_id}: gagal dikirim ({exc})")
    return results


async def notify_engineers(update, context):
    """Manual resend of the real current ticket queues."""
    results = await broadcast_engineers(context.bot)
    await update.effective_message.reply_text("Hasil pengiriman:\n" + "\n".join(results))


async def scheduled_notify_engineers(context):
    """JobQueue callback for the daily blast."""
    results = await broadcast_engineers(context.bot)
    print("Daily engineer broadcast: " + "; ".join(results))
