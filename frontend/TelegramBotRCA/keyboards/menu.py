from telegram import ReplyKeyboardMarkup


def main_menu():
    keyboard = [
        ["👨‍💼 Management"],
        ["👷 Engineer Field"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

data = {"sectorId"}

def management_menu():
    keyboard = [
        ["📈 Grafik RCA"],
        ["🏢 Cek Per Distrik"],
        ["🌎 Overview"],
        ["⬅️ Kembali"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def engineer_menu():
    keyboard = [
        ["🎫 Ambil Ticket"],
        ["✅ Solve Ticket"],
        ["📝 RCA"],
        ["📄 RCA Detail"],
        ["⬅️ Kembali"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )