import telegram

from miptbot.settings import TELEGRAM_TOKEN, TELEGRAM_LOGS_CHAT_ID, DEBUG

bot = telegram.Bot(TELEGRAM_TOKEN)

def send_text(text, reply_markup=None, parse_mode=telegram.ParseMode.HTML):
    debug_pref = "🛠" if DEBUG else ""
    text_to_send = debug_pref + text

    return bot.send_message(
        chat_id=TELEGRAM_LOGS_CHAT_ID,
        text=text_to_send,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
