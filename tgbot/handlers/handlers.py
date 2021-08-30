"""
    This Bot is very cool.
"""

import re
import string
import random
import logging
import telegram

from tgbot.models import User
from tgbot.handlers.logs import send_text
from tgbot.handlers import texts


from OLD.modules.constants import (
    USER_DATA_KEYS, MAIN_CHAT_ID,
    SMTP_SERVER, SMTP_PORT,
    N_MINUTES_PER_INVITE, SMTP_SINGIN, N_CODE
)

from OLD.modules.utilities import *


def make_kb(keys, one_time_keyboard=True):
    return telegram.ReplyKeyboardMarkup(
        keys,
        resize_keyboard=True,
        one_time_keyboard=one_time_keyboard,
    )


def gen_random_string(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def main_menu(update, context):
    user = User.get_user(update, context)
    send_text(f"New user: {user}")
    update.message.reply_text(
        f'Привет 👋 '
        f'Этот бот поможет вам добавиться в общий чат физтехов, '
        f'даст информацию о том, какие есть тематические '
        f'чаты и каналы на Физтехе.',
        reply_markup=telegram.ReplyKeyboardMarkup([
                ['Добавиться в чат'],
                ['Показать чаты', 'Показать сервисы'],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


def add_to_chat(update, context):
    user = User.get_user(update, context)

    # user.is_in_chat = True
    # user.save()

    if user.is_in_chat or user.status == "approved":
        update.message.reply_text(
            'Вы уже были добавлены в чат. \n'
            'В случае возникновения проблем, '
            'обратитесь к модератору @realkostin.',
            reply_markup=telegram.ReplyKeyboardMarkup(
                [['Показать чаты', 'Показать сервисы']],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        )
    else:
        update.message.reply_text(
            'Чтобы добавить вас в чат, необходимо удостовериться, что вы из МФТИ. '
            'Напишите свою почту на домене <b>phystech.edu</b> '
            'и мы вышлем на неё секретный код. '
            'После этого, напишите сюда код с электронной почты '
            'и вам дадут ссылку на добавление в чат.',
            reply_markup=telegram.ReplyKeyboardRemove(),
            parse_mode=telegram.ParseMode.HTML
        )


def show_blogs(update, context):
    update.message.reply_text(
        texts.BLOGS,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=telegram.ReplyKeyboardMarkup(
            [['Добавиться в чат', 'Показать сервисы']],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


def show_chats(update, context):
    update.message.reply_text(
        texts.CHATS,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=telegram.ReplyKeyboardMarkup(
            [['Добавиться в чат', 'Показать сервисы']],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


def show_services(update, context):
    update.message.reply_text(
        texts.SERVICES,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=telegram.ReplyKeyboardMarkup(
            [['Добавиться в чат', 'Показать чаты']],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


def reply_start(update, context):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    LOGGER.info(f'Show chats.')
    update.message.reply_text('Иногда, чтобы начать всё сначала, достаточно нажать /start.',
                              reply_markup=telegram.ReplyKeyboardRemove())
    # return MAIN_MENU


def wait_for_email(update, context):
    user = User.get_user(update, context)
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    email_input = update.message.text.strip().lower()

    # Check email is in db
    if user.email is not None and email_input != user.email:
        LOGGER.info(f'Another email exist.')
        return update.message.reply_text(
            f'Хммм. Есть информация, что ваша почта другая: {user.email}.\n'
            f'Скорее всего, это связано с тем, что вы вводили её ранее.'
            f'Если вы опечатались или возникла другая ошибка - напишите @lego1as',
            reply_markup=make_kb([
                ['Добавиться в чат'], ['Показать чаты', 'Показать сервисы']
            ])
        )

    LOGGER.info(f'Record email {email_input}.')
    user.code = gen_random_string(N_CODE)
    user.email = email_input
    user.save()

    message_text = f'Ваш пригласительный код: {user.code}.'
    sent = send_email(email_input, message_text, LOGGER)
    if sent:
        LOGGER.info(f'Successful send message to {user.email}.')
    else:
        LOGGER.error(f'Cannot send message to {user.email}.')

    # TODO: Solve markdown problem
    update.message.reply_text(
        f'Мы отправили письмо на почту **{user.email}**.\n'
        'Пришлите код сообщением сюда.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
    )


# TODO: Add to handler
def wrong_email(update, context):
    update.message.reply_text(
        'Где-то ошибка, введите ещё раз, пожалуйста.',
        reply_markup=telegram.ReplyKeyboardRemove(),
    )


def wait_for_code(update, context):
    user = User.get_user(update, context)
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    LOGGER.info(f'Code reception.')

    code = update.message.text
    if code == user.code:
        user.status = "approved"
        update.message.reply_text('Проверка прошла успешно!\n'
                                  f'Пожалуйста, ознакомьтесь с правилами группы: \n'
                                  f'\n{RULES}.\n'
                                  'Напишите "Да", если вы согласны с правилами группы',
                                  reply_markup=telegram.ReplyKeyboardRemove())
    else:
        update.message.reply_text('Неверный код. Введите ещё раз.\n'
                                  f'Осталось попыток: {attempts_left}',
                                  reply_markup=ReplyKeyboardRemove())


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
