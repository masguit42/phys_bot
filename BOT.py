"""
    This Bot is very cool.
"""

from telegram.ext import RegexHandler
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, ConversationHandler)

from modules.constants import (
    MAIN_MENU,
    ADD_TO_CHAT,
    WAIT_FOR_EMAIL, WAIT_FOR_CODE,
    SEND_INVITATION,
    BOT_TOKEN)

from modules.bot_methods import (
    add_to_chat, done, error, help_menu,
    main_menu, send_invitation, show_chats,
    show_services, wait_for_code, wait_for_email,
    reply_start)


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
                CommandHandler('start', main_menu,  pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, reply_start),
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
            SEND_INVITATION: [
                RegexHandler('^(Спасибочки)$', main_menu, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu, pass_user_data=True),
            ]
        },
        fallbacks=[RegexHandler('^Спасибо', done)]
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
