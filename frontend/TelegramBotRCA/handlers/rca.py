from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from data.dummy_rca_detail import DUMMY_RCA_DETAIL
from data.dummy_tickets import DUMMY_TICKETS


async def select_rca(update, context):

    query = update.callback_query

    await query.answer()

    rca = query.data.replace("rca_", "")

    context.user_data["rca"] = rca

    details = DUMMY_RCA_DETAIL.get(rca, [])

    keyboard = []

    for detail in details:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=detail,
                    callback_data=f"detail_{detail}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=(
            f"📄 RCA : {rca}\n\n"
            "Silakan pilih RCA Detail."
        ),
        reply_markup=reply_markup
    )


async def select_rca_detail(update, context):

    query = update.callback_query

    await query.answer()

    detail = query.data.replace("detail_", "")

    incident = context.user_data["ticket"]

    rca = context.user_data["rca"]

    for ticket in DUMMY_TICKETS:

        if ticket["incident"] == incident:

            ticket["rca"] = rca

            ticket["rca_detail"] = detail

            ticket["checked"] = True

            break

    await query.edit_message_text(

        text=(
            "✅ Ticket berhasil di-check.\n\n"
            f"Incident : {incident}\n"
            f"RCA : {rca}\n"
            f"RCA Detail : {detail}"
        )

    )