"""
    Telegram event handlers
"""

import telegram
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from miptbot.settings import TELEGRAM_TOKEN

from tgbot.handlers import error, handlers


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """

    # Broadcast
    dp.add_handler(CommandHandler("start", handlers.main_menu))
    dp.add_handler(CommandHandler("menu", handlers.main_menu))
    dp.add_handler(CommandHandler("chats", handlers.show_chats))

    dp.add_handler(CallbackQueryHandler(handlers.authorize, pattern='authorize'))
    dp.add_handler(CallbackQueryHandler(handlers.show_chats, pattern='chats'))
    dp.add_handler(CallbackQueryHandler(handlers.show_blogs, pattern='blogs'))
    dp.add_handler(CallbackQueryHandler(handlers.show_services, pattern='services'))

    dp.add_handler(MessageHandler(Filters.regex('^(\w|\.|-)+@phystech\.edu$'), handlers.get_email))
    dp.add_handler(MessageHandler(Filters.regex('^[A-Z0-9]{6}$'), handlers.get_code))
    dp.add_handler(CallbackQueryHandler(handlers.send_invitation, pattern='agree'))
    dp.add_handler(CallbackQueryHandler(handlers.main_menu, pattern='fun'))

    dp.add_handler(MessageHandler(Filters.regex('^(Добавиться в чат)$'), handlers.main_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Показать чаты)$'), handlers.main_menu))
    dp.add_handler(MessageHandler(Filters.regex('^(Показать сервисы)$'), handlers.main_menu))

    dp.add_handler(MessageHandler(Filters.text, handlers.main_menu))

    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    updater.start_polling()
    updater.idle()


def process_telegram_event(update_json):
    update = telegram.Update.de_json(update_json, bot)
    dispatcher.process_update(update)


# Global variable - best way I found to init Telegram bot
bot = telegram.Bot(TELEGRAM_TOKEN)
dispatcher = setup_dispatcher(Dispatcher(bot, None, workers=0, use_context=True))
