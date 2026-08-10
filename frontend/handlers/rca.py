from api_client import BackendAPIError, get_rca_options, submit_rca


async def input_rca(update, context):
    if not context.user_data.get("waiting_rca"):
        return
    message = update.message.text.strip()
    if not message.isdigit():
        await update.message.reply_text("❌ Masukkan nomor RCA.")
        return

    try:
        options = context.user_data.get("rca_options") or await get_rca_options()
    except BackendAPIError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    categories = list(options)
    number = int(message)
    if number < 1 or number > len(categories):
        await update.message.reply_text("❌ Nomor RCA tidak tersedia.")
        return

    rca = categories[number - 1]
    context.user_data.update(rca=rca, rca_options=options, waiting_rca=False, waiting_detail=True)
    details = options[rca]
    text = f"✅ RCA dipilih: {rca}\n\nSilakan pilih RCA Detail.\n\n"
    text += "\n".join(f"{index}. {detail}" for index, detail in enumerate(details, start=1))
    text += "\n\nBalas dengan nomor RCA Detail."
    await update.message.reply_text(text)


async def input_rca_detail(update, context):
    if not context.user_data.get("waiting_detail"):
        return
    message = update.message.text.strip()
    if not message.isdigit():
        await update.message.reply_text("❌ Masukkan nomor RCA Detail.")
        return

    rca = context.user_data["rca"]
    details = context.user_data["rca_options"][rca]
    number = int(message)
    if number < 1 or number > len(details):
        await update.message.reply_text("❌ Nomor RCA Detail tidak tersedia.")
        return

    rca_detail = details[number - 1]
    ticket = context.user_data["ticket"]
    try:
        await submit_rca(ticket["ticket_id"], rca, rca_detail)
    except BackendAPIError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    context.user_data["waiting_detail"] = False
    context.user_data.pop("ticket", None)
    context.user_data.pop("rca", None)
    context.user_data.pop("rca_options", None)

    await update.message.reply_text(
        "✅ RCA berhasil disimpan.\n\n"
        f"Tiket: #{ticket['ticket_id']}\nRCA: {rca}\nRCA Detail: {rca_detail}"
    )

    # Refresh immediately so the engineer sees the latest ticket queue.
    from handlers.ticket import show_ticket_dashboard
    await show_ticket_dashboard(update, context)
