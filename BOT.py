"""
    This Bot uses the Updater class to handle the bot.
    First, a few callback functions are defined. Then, those functions are passed to
    the Dispatcher and registered at their respective places.
    Then, the bot is started and runs until we press Ctrl-C on the command line.
    Usage:
    Example of a bot-user conversation using ConversationHandler.
    Send /start to initiate the conversation.
    Press Ctrl-C on the command line or send a signal to the process to stop the
    bot.
"""

from telegram.ext import RegexHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from modules.bot_methods import *
from modules.constants import (
    MAIN_MENU, SHOW_CHATS, SHOW_SERVICES,
    ADD_TO_CHAT,
    WAIT_FOR_EMAIL, WAIT_FOR_CODE,
    BOT_TOKEN)

from modules.bot_methods import (
    add_to_chat, done, error, help_menu,
    main_menu, send_invitation, show_chats,
    show_services, wait_for_code, wait_for_email)



# # Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
#
# logger = logging.getLogger(__name__)

# PROFILE_DB = ProfileDB("data/main.sqlite")


def main():

    with open(BOT_TOKEN, 'r') as f:
        token = f.read().split('\n')[0]

    updater = Updater(token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', main_menu, pass_user_data=True)],
        states={
            MAIN_MENU: [
                RegexHandler('^(Добавиться в чат)$', add_to_chat, pass_user_data=True),
                RegexHandler('^(Показать чаты)$', show_chats),
                RegexHandler('^(Показать сервисы)$', show_services),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu,  pass_user_data=True),
            ],
            ADD_TO_CHAT: [
                MessageHandler(Filters.text, wait_for_email, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
            ],
            WAIT_FOR_EMAIL: [
                MessageHandler(Filters.text, wait_for_code, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
            ],
            WAIT_FOR_CODE: [
                MessageHandler(Filters.text, send_invitation, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
            ],
            SHOW_CHATS: [
                RegexHandler('^(Чаты)$', show_chats, pass_user_data=True),
                CommandHandler('start', main_menu,  pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu, pass_user_data=True),
            ],
            SHOW_SERVICES: [
                RegexHandler('^(Сервисы)$', show_services, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu, pass_user_data=True),
            ],
        },
        fallbacks=[RegexHandler('^Спасибо', done, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
