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

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, ParseMode

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import RegexHandler,CallbackQueryHandler,ConversationHandler

import re
import json
import logging
import numpy as np

from utilities import encode_lp, send_email, make_kb, gen_random_string

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

# keyboard3 = [[InlineKeyboardButton("Да", callback_data='1'),
#               InlineKeyboardButton("Нет", callback_data='2')]]

# reply_markup3 = InlineKeyboardMarkup(keyboard3, one_time_keyboard=True)


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text("%s" % facts_to_str(user_data))
    admin_id=56234431
    bot.sendMessage(chat_id=admin_id, text=facts_to_str(user_data))
    user_data.clear()
    return ConversationHandler.END

def help_menu(bot, update):
    update.message.reply_text("Suk, nu privet!")

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

MAIN_MENU, SHOW_FORUMS, ADD_TO_CHAT, SENT_EMAIL, WAIT_FOR_EMAIL, WAIT_FOR_CODE, *_ = range(100)
ADMIN_ID = 150153954
N_CODE = 6


def main_menu(bot, update, user_data):
    print(update.message.from_user)
    user_data['first_name'] = update.message.from_user.first_name
    user_data['last_name'] = update.message.from_user.last_name

    update.message.reply_text(
        '\n'.join(['Привет, {}.'.format(user_data['first_name']),
                   'Этот бот поможет вам добавиться в общий чат физтехов,',
                   'даст информацию, какие есть тематические чаты и каналы',
                   'на физтехе. ']),
        reply_markup=make_kb([  ['Добавиться в чат'],
                                ['Показать каналы/чаты']]),
    )
    return MAIN_MENU


def add_to_chat(bot, update, user_data):
    print(update.message.from_user)
    if 'accepted' in user_data.keys():
        return MAIN_MENU
    else:
        update.message.reply_text(
            '\n'.join([ 'Чтобы добавить тебя в чат, необходимо удостовериться, что ты с МФТИ.',
                        'Напиши свою почту на домене `phystech.edu`,',
                        'и мы вышлем тебе секретный код на неё.',
                        'После этого, напиши код с электронной почты в переписку',
                        'и тебе дадут ссылку на добавление в чат.']),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ADD_TO_CHAT


def show_forums(bot, update, user_data):
    update.message.reply_text('Вы хотите посмотреть каналы или чаты?',
                              reply_markup=make_kb([['Каналы'],
                                                    ['Чаты']]))
    return SHOW_FORUMS


def wait_for_email(bot, update, user_data):
    text = update.message.text
    if re.match(r'^(\w|\.)+@phystech\.edu$', text):
        code = gen_random_string(N_CODE)
        user_data['code'] = code
        user_data['email'] = text
        concat_string = code + user_data['first_name'] + user_data['last_name']
        user_data['hash'] = hash(concat_string)

        send_email(user_data['email'], user_data['code'])
        update.message.reply_text(
            'Мы отправили письмо на почту `{}`'.format(user_data['email'])
        )
        print(user_data)
        return WAIT_FOR_EMAIL
    else:
        update.message.reply_text('Где-то ошибка, введите ещё раз, пожалуйста.')
        return ADD_TO_CHAT

def wait_for_code(bot, update):
    return help_menu(bot, update)



# bot.sendMessage(chat_id=ADMIN_ID, text=facts_to_str((user_data)) + '\n')


def main():
    with open('token.txt', 'r') as f:
        TOKEN = f.read().split('\n')[0]
    with open('request_kwargs.json') as f:
        rkwargs = f.read().replace('\n', '').replace('  ', '')
        REQUEST_KWARGS = json.loads(rkwargs)
        del rkwargs

    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', main_menu, pass_user_data=True)],
        states={
            MAIN_MENU: [
                RegexHandler('^(Добавиться в чат)$', add_to_chat, pass_user_data=True),
                RegexHandler('^(Показать каналы/чаты)$', show_forums, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu,  pass_user_data=True),
            ],
            ADD_TO_CHAT: [
                MessageHandler(Filters.text, wait_for_email, pass_user_data=True),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
            ],
            WAIT_FOR_CODE: [
                MessageHandler(Filters.text, wait_for_code),
                CommandHandler('start', main_menu, pass_user_data=True),
                CommandHandler('help', help_menu),
            ],
            SHOW_FORUMS: [
                RegexHandler('^(Каналы)$', add_to_chat, pass_user_data=True),
                RegexHandler('^(Чаты)$', show_forums, pass_user_data=True),
                CommandHandler('start', main_menu,  pass_user_data=True),
                CommandHandler('help', help_menu),
                MessageHandler(Filters.text, main_menu, pass_user_data=True),
            ],
        },
        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
