from telegram import ReplyKeyboardMarkup


def main_menu():
    keyboard = [
        ["👨‍💼 Management"],
        ["👷 Engineer Field"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def management_menu():
    keyboard = [
        ["📈 Grafik RCA"],
        ["🏢 Cek Per Distrik"],
        ["🌎 Overview"],
        ["⬅️ Kembali"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def engineer_menu():
    keyboard = [
        ["Ticket History"],
        ["🎫 View Ticket"],
        ["⬅️ Kembali"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
