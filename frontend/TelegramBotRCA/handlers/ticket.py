from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from data.dummy_tickets import DUMMY_TICKETS
from data.dummy_rca import DUMMY_RCA


async def view_tickets(update, context):

    keyboard = []

    for ticket in DUMMY_TICKETS:

        if not ticket["checked"]:

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{ticket['incident']} | {ticket['customer']}",
                        callback_data=f"ticket_{ticket['incident']}"
                    )
                ]
            )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 Silakan pilih ticket.",
        reply_markup=reply_markup
    )


async def select_ticket(update, context):

    query = update.callback_query

    await query.answer()

    incident = query.data.replace("ticket_", "")

    ticket = next(
        (
            t for t in DUMMY_TICKETS
            if t["incident"] == incident
        ),
        None
    )

    if ticket is None:

        await query.edit_message_text(
            "Ticket tidak ditemukan."
        )

        return

    context.user_data["ticket"] = incident

    keyboard = []

    for rca in DUMMY_RCA:

        keyboard.append(
            [
                InlineKeyboardButton(
                    rca,
                    callback_data=f"rca_{rca}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(

        text=(
            "📄 DETAIL TICKET\n\n"
            f"Incident : {ticket['incident']}\n"
            f"Customer : {ticket['customer']}\n"
            f"Site : {ticket['site']}\n"
            f"District : {ticket['district']}\n"
            f"Status : {ticket['status']}\n\n"
            "Silakan pilih RCA."
        ),

        reply_markup=reply_markup
    )