"""Global NOP-scoped, read-only dashboard for MasterManager users."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from api_client import BackendAPIError, get_master_analytics


MASTER_MENU = [["Show Graph"], ["NOP Detail"]]
MASTER_DETAIL_MENU = [["Show Graph"], ["NOP Detail"], ["Active Tickets"], ["Back"]]
GRAPH_PERIOD_MENU = [["7 days", "30 days"], ["2 months"], ["Back"]]


def _menu(detail=False):
    return ReplyKeyboardMarkup(
        MASTER_DETAIL_MENU if detail else MASTER_MENU,
        resize_keyboard=True, one_time_keyboard=False, is_persistent=True,
    )


async def show_master_dashboard(update: Update, context):
    context.user_data["master_mode"] = True
    context.user_data["master_screen"] = "global"
    context.user_data.pop("master_current_npo", None)
    try:
        from graph_view import build_manager_analytics_chart
        payload = await get_master_analytics(update.effective_user.id, days=30)
        chart = build_manager_analytics_chart(payload)
    except BackendAPIError as exc:
        await update.effective_message.reply_text(f"Error: {exc}", reply_markup=_menu())
        return
    except ImportError:
        await update.effective_message.reply_text("Graph View membutuhkan matplotlib.", reply_markup=_menu())
        return
    context.user_data["master_npos"] = [item["district"] for item in payload.get("districts", [])]
    if chart is None:
        await update.effective_message.reply_text("Belum ada data historis untuk grafik.", reply_markup=_menu())
        return
    await update.effective_message.reply_photo(
        photo=chart,
        caption="GRAPH VIEW — semua NOP\nActive/closed, RCA-completed, service-completed, dan response time per NOP.",
        reply_markup=_menu(),
    )


async def prompt_master_graph(update, context):
    context.user_data["master_waiting_graph_period"] = True
    await update.effective_message.reply_text(
        "Pilih periode Graph View:",
        reply_markup=ReplyKeyboardMarkup(GRAPH_PERIOD_MENU, resize_keyboard=True, is_persistent=True),
    )


async def show_master_graph(update, context, days):
    try:
        from graph_view import build_manager_analytics_chart
        payload = await get_master_analytics(
            update.effective_user.id,
            context.user_data.get("master_current_npo"),
            days=days,
        )
        chart = build_manager_analytics_chart(payload)
    except (BackendAPIError, ImportError) as exc:
        await update.effective_message.reply_text(f"Graph tidak tersedia: {exc}", reply_markup=_menu(bool(context.user_data.get("master_current_npo"))))
        return
    if chart is None:
        await update.effective_message.reply_text("Belum ada data historis untuk grafik.", reply_markup=_menu(True))
        return
    await update.effective_message.reply_photo(
        photo=chart,
        caption=f"GRAPH VIEW — {payload['npo']} — {days} hari terakhir",
        reply_markup=_menu(True),
    )


async def prompt_master_npo(update, context):
    npos = context.user_data.get("master_npos", [])
    if not npos:
        try:
            payload = await get_master_analytics(update.effective_user.id, days=30)
            npos = [item["district"] for item in payload.get("districts", [])]
            context.user_data["master_npos"] = npos
        except BackendAPIError as exc:
            await update.effective_message.reply_text(f"Error: {exc}")
            return
    context.user_data["master_waiting_npo"] = True
    choices = "\n".join(f"{i}. {npo}" for i, npo in enumerate(npos, 1))
    await update.effective_message.reply_text(
        "Pilih NOP dengan membalas nomornya:\n\n" + choices,
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_master_npo(update, context, npo):
    context.user_data["master_current_npo"] = npo
    context.user_data["master_screen"] = "npo"
    await show_master_graph(update, context, 30)
    context.user_data["ticket_view_role"] = "master_manager"
    context.user_data["ticket_view_district"] = npo
    await update.effective_message.reply_text(
        f"NOP DETAIL — {npo}\nPilih Active Tickets untuk melihat tiket aktif lintas district.",
        reply_markup=_menu(True),
    )


async def show_master_tickets(update, context):
    from handlers.ticket import show_ticket_dashboard
    context.user_data["ticket_view_role"] = "master_manager"
    context.user_data["ticket_view_district"] = context.user_data.get("master_current_npo")
    await show_ticket_dashboard(update, context, interactive=False)
    await update.effective_message.reply_text("VIEW TICKETS\nRead-only ticket view.", reply_markup=_menu(True))


async def process_master_input(update, context):
    message = update.message.text.strip() if update.message else ""
    if context.user_data.get("master_waiting_graph_period"):
        if message == "Back":
            context.user_data["master_waiting_graph_period"] = False
            await show_master_dashboard(update, context)
            return
        periods = {"7 days": 7, "30 days": 30, "2 months": 60}
        if message not in periods:
            await update.message.reply_text("Pilih 7 days, 30 days, atau 2 months.")
            return
        context.user_data["master_waiting_graph_period"] = False
        await show_master_graph(update, context, periods[message])
        return
    if context.user_data.get("master_waiting_npo"):
        if not message.isdigit():
            await update.message.reply_text("Masukkan nomor NOP.")
            return
        npos = context.user_data.get("master_npos", [])
        number = int(message)
        if number < 1 or number > len(npos):
            await update.message.reply_text("Nomor NOP tidak ditemukan.")
            return
        context.user_data["master_waiting_npo"] = False
        await show_master_npo(update, context, npos[number - 1])
        return
    if message == "Show Graph":
        await prompt_master_graph(update, context)
    elif message == "NOP Detail":
        await prompt_master_npo(update, context)
    elif message == "Active Tickets":
        await show_master_tickets(update, context)
    elif message == "Back":
        await show_master_dashboard(update, context)
