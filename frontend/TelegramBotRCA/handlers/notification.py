"""Commands for sending ticket assignments to engineers."""

from telegram.error import TelegramError

from api_client import BackendAPIError, get_engineers, get_mock_engineer_tickets


def _ticket_line(ticket):
    identifiers = ticket["identifiers"]
    if ticket["ticket_type"] == "ZP":
        identity = f"eNodeB {identifiers['enodeb_id']}/Cell {identifiers['cell_id']}"
    else:
        identity = f"LAC {identifiers['lac']}/CI {identifiers['ci']}"
    return f"• #{ticket['ticket_id']} — {ticket['site_id']} ({identity}), aging {ticket['aging']} hari"


async def notify_engineers(update, context):
    """Send each mock engineer their five currently assigned mock tickets."""
    try:
        engineers = (await get_engineers())["engineers"]
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"❌ {exc}")
        return

    results = []
    for telegram_id in engineers:
        try:
            assignment = await get_mock_engineer_tickets(telegram_id)
        except BackendAPIError as exc:
            results.append(f"{telegram_id}: gagal mengambil tiket ({exc})")
            continue

        tickets = assignment["tickets"]
        message = (
            f"📋 PENUGASAN TIKET\n\n"
            f"District: {assignment['district']}\n"
            f"Total: {len(tickets)} tiket\n\n"
            + "\n".join(_ticket_line(ticket) for ticket in tickets)
            + "\n\nSilakan buka bot dan pilih 🎫 View Ticket untuk memproses RCA."
        )
        try:
            await context.bot.send_message(chat_id=telegram_id, text=message)
            results.append(f"{telegram_id}: terkirim ({len(tickets)} tiket)")
        except TelegramError as exc:
            # Telegram rejects a chat that has never initiated the bot.
            results.append(f"{telegram_id}: gagal dikirim ({exc})")

    await update.effective_message.reply_text("Hasil pengiriman:\n" + "\n".join(results))
