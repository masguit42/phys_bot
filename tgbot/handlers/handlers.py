"""
    This Bot is very cool.
"""

import re
import string
import random
import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from tgbot.models import User
from tgbot.handlers.logs import send_text
from tgbot.handlers import texts


from OLD.modules.constants import (
    USER_DATA_KEYS, MAIN_CHAT_ID,
    SMTP_SERVER, SMTP_PORT,
    N_MINUTES_PER_INVITE, SMTP_SINGIN, N_CODE
)

from OLD.modules.utilities import *

import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEBUG = True


def make_kb(keys, one_time_keyboard=True):
    return telegram.ReplyKeyboardMarkup(
        keys,
        resize_keyboard=True,
        one_time_keyboard=one_time_keyboard,
    )


def make_kb_inline(keys, ):
    markup = telegram.InlineKeyboardMarkup()
    button0 = telegram.InlineKeyboardButton("Авторизоваться", callback_data='auth')
    # markup.add(button0)


def gen_random_string(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


# from ohld
def telegram_message_remove_buttons(user_id, message_id):
    bot = telegram.Bot(TELEGRAM_TOKEN)
    try:
        bot.editMessageReplyMarkup(
            chat_id=user_id,
            message_id=message_id,
        )
    except BadRequest:
        pass  # message was already deleted


def telegram_message_delete(user_id, message_id):
    bot = telegram.Bot(TELEGRAM_TOKEN)
    try:
        bot.deleteMessage(chat_id=user_id, message_id=message_id)
    except Exception as e:  # if can't delete - at least remove buttons
        # logger.warning(f"Can't remove message of user_id={user_id}, reason: {e}")
        telegram_message_remove_buttons(user_id, message_id)


def _delete_last_message(query):
    """ Delete last message in chat """
    if query is not None:
        user_id = query.message.chat_id
        message_id = query.message.message_id
        if DEBUG:
            telegram_message_delete(user_id, message_id)
        else:
            telegram_message_delete.delay(user_id, message_id)
# from ohld


def main_menu(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    context.bot.send_message(
        chat_id=chat_id,
        text='👋',
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
    if user.authorized:
        context.bot.send_message(
            chat_id=chat_id,
            text='Хотите посмотреть, какие есть чаты/сервисы/блоги у физтехов?',
            reply_markup=InlineKeyboardMarkup.from_column(
                [
                    InlineKeyboardButton("Чаты", callback_data='chats'),
                    InlineKeyboardButton("Сервисы", callback_data='services'),
                    InlineKeyboardButton("Блоги", callback_data='blogs'),
                ]
            )
        )
    else:
        send_text(f'New user: {user}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Этот бот позволит вам добавиться в общий чат физтехов, '
                 'даст информацию о том, какие есть '
                 'чаты, каналы и сервисы в телеграме на Физтехе.',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('Авторизоваться 👉👌🏻', callback_data='authorize')
            )
        )


def authorize(update, context):
    user = User.get_user(update, context)

    if user.authorized:
        show_interesting(update, context)
    else:
        chat_id = user.user_id
        send_text(f'authorize: {user}')
        user.in_authorizing = True
        user.save()
        context.bot.send_message(
            chat_id=chat_id,
            text='Давай удостоверимся, что ты из МФТИ. '
                 'Напиши свою почту на домене <b>phystеch.еdu</b> '
                 'и мы вышлем на неё секретный код. '
                 'Отправь сюда код с электронной почты '
                 'и ты получишь уникальный доступ к чатикам 😉',
            parse_mode=telegram.ParseMode.HTML
        )


def show_blogs(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if user.username == 'realkostin' or user.authorized: # TODO: Remove hardcode
        _delete_last_message(update.callback_query)
        context.bot.send_message(
            chat_id=chat_id,
            text=texts.BLOGS,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_column(
                [
                    InlineKeyboardButton("Чаты", callback_data='chats'),
                    InlineKeyboardButton("Сервисы", callback_data='services'),
                    InlineKeyboardButton("Блоги", callback_data='blogs'),
                ]
            )
        )
    else:
        caught_unauthorized(update, context)


def show_chats(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if user.username == 'realkostin' or user.authorized:
        _delete_last_message(update.callback_query)
        context.bot.send_message(
            chat_id=chat_id,
            text=texts.CHATS,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_column(
                [
                    InlineKeyboardButton("Чаты", callback_data='chats'),
                    InlineKeyboardButton("Сервисы", callback_data='services'),
                    InlineKeyboardButton("Блоги", callback_data='blogs'),
                ]
            )
        )
    else:
        caught_unauthorized(update, context)


def show_services(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if user.username == 'realkostin' or user.authorized:
        _delete_last_message(update.callback_query)
        context.bot.send_message(
            chat_id=chat_id,
            text=texts.SERVICES,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup.from_column(
                [
                    InlineKeyboardButton("Чаты", callback_data='chats'),
                    InlineKeyboardButton("Сервисы", callback_data='services'),
                    InlineKeyboardButton("Блоги", callback_data='blogs'),
                ]
            )
        )
    else:
        caught_unauthorized(update, context)


def show_interesting(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    context.bot.send_message(
        chat_id=chat_id,
        text='😀'
    )
    context.bot.send_message(
        chat_id=chat_id,
        text='Посмотри, что интересного есть у физтехов',
        reply_markup=InlineKeyboardMarkup.from_column(
            [
                InlineKeyboardButton("Чаты", callback_data='chats'),
                InlineKeyboardButton("Сервисы", callback_data='services'),
                InlineKeyboardButton("Блоги", callback_data='blogs'),
            ]
        )
    )


def caught_unauthorized(update, context):
    update.message.reply_text('🤔')
    authorize(update, context)


# def reply_start(update, context):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     LOGGER.info(f'Show chats.')
#     update.message.reply_text('Иногда, чтобы начать всё сначала, достаточно нажать /start.',
#                               reply_markup=telegram.ReplyKeyboardRemove())


def get_email(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if not user.in_authorizing:
        send_text(f'in_authorizing: {user.in_authorizing}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Не могу разобрать, что-то на физтеховском. '
                 'Попробуй начать авторизацию заново',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('Авторизоваться 👉👌🏻', callback_data='authorize')
            )
        )
    else:
        # LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
        email_input = update.message.text.strip().lower()
        send_text(f'in_authorizing: {user.in_authorizing}')
        # Check email is in db
        # if user.email is not None and email_input != user.email:
        #     LOGGER.info(f'Another email exist.')
        #     return update.message.reply_text(
        #         f'Хммм. Есть информация, что у тебя другая почта: {user.email}.\n'
        #         f'Скорее всего, это связано с тем, что ты вводили именно её ранее.'
        #         f'Если опечатался или возникла другая ошибка - напиши @realkostin',
        #         reply_markup=make_kb([
        #             ['Добавиться в чат'], ['Показать чаты', 'Показать сервисы']
        #         ])
        #     )

        # LOGGER.info(f'Record email {email_input}.')
        user.code = gen_random_string(N_CODE)
        send_text(f'code: {user.code}, len: {len(user.code)}')
        user.email = email_input
        user.save()

        message_text = f'Ваш пригласительный код: {user.code}.'
        sent = send_email(email_input, message_text, LOGGER)
        if sent:
            LOGGER.info(f'Successful send message to {user.email}.')
        else:
            LOGGER.error(f'Cannot send message to {user.email}.')

        # TODO: Solve markdown problem
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Мы отправили письмо на почту <b>{user.email}<b>.\n'
                 'Пришлите код сообщением сюда.',
            parse_mode=telegram.ParseMode.HTML,
        )


# TODO: Add to handler
def wrong_email(update, context):
    update.message.reply_text(
        'Где-то ошибка, введите ещё раз, пожалуйста.',
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


# def wait_for_code(update, context):
#     user = User.get_user(update, context)
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     LOGGER.info(f'Code reception.')
#
#     code = update.message.text
#     if code == user.code:
#         user.status = "approved"
#         update.message.reply_text('Проверка прошла успешно!\n'
#                                   f'Пожалуйста, ознакомьтесь с правилами группы: \n'
#                                   f'\n{RULES}.\n'
#                                   'Напишите "Да", если вы согласны с правилами группы',
#                                   reply_markup=telegram.ReplyKeyboardRemove())
#     else:
#         update.message.reply_text('Неверный код. Введите ещё раз.\n'
#                                   f'Осталось попыток: {attempts_left}',
#                                   reply_markup=ReplyKeyboardRemove())


def send_invitation(update, context):
    user = User.get_user(update, context)
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

    if update.message.text == "Да":
        LOGGER.info(f'Agree with rules.')
        invite_link = bot.exportChatInviteLink(CHANNEL_ID)
        user.invite_link = invite_link
        # TODO: Solve markdown problem
        update.message.reply_text('Добро пожаловать в канал Физтех.Важное: \n'
                                  f'{invite_link}\n'
                                  'Внизу с правой стороны будет кнопка для перехода в чат **Phystech. No Flood**\n'
                                  'Пожалуйста, нажмите кнопку, как добавитесь в чат.',
                                  reply_markup=make_kb([['Спасибочки']]),
                                  parse_mode=ParseMode.MARKDOWN)
        LOGGER.info(f'Link sent.')

        # Send log to public channel
        bot.sendMessage(chat_id=LOGS_CHANNEL_ID,
                        text=INVITE_LINK_MSG.format(
                            first_name=user.first_name,
                            last_name=user.last_name,
                            username=user.username,
                            uid=user.id))

        # TODO: Record profile
    else:
        LOGGER.warning(f'Misagree with rules.')
        update.message.reply_text('Осталось только согласиться с правилами. Ну же.')


def help_menu(update, context):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    LOGGER.info(f'Use help menu.')
    update.message.reply_text("По всем возникшим вопросам и предложениям писать @realkostin",
                              reply_markup=make_kb([['Добавиться в чат'],
                                                    ['Показать чаты', 'Показать сервисы']]))


def error(update, context):
    if not update is None:
        LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    else:
        LOGGER = logging.getLogger('root')
    # LOGGER.error(f'Update "{update}" caused error "{error}"')
