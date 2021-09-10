"""
    This Bot is very cool.
"""
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


from tgbot.models import User
from tgbot.handlers.logs import send_text
from tgbot.handlers import texts

from tgbot.handlers.bot_utils import gen_random_string, _delete_last_message, send_email

from tgbot.handlers.bot_constants import (
    LOGS_CHANNEL_ID, N_CODE,
    CHANNEL_ID, ADMIN_ID
)


def main_menu(update, context):
    user, created = User.get_user_and_created(update, context)
    # DEBUG
    # raise Exception(f'{update}')
    if not created:
        if update.effective_message.chat.type != 'private':
            return None

    chat_id = user.user_id

    if chat_id == int(ADMIN_ID):
        user.authorized = False  # TODO: Remove debug with admin.
        user.in_authorizing = False
        user.save()

    if user.in_authorizing:
        wrong_email(update, context)
    elif not user.authorized:
        context.bot.send_message(
            chat_id=chat_id,
            text='👋',
            reply_markup=telegram.ReplyKeyboardRemove(),
        )
        if created:
            link_user = f'<a href="tg://user?id={user.user_id}">{user}</a>'
            send_text(f'New user: {link_user}')
        context.bot.send_message(
            chat_id=chat_id,
            text='Этот бот позволит вам добавиться в общий чат физтехов, '
                 'даст информацию о том, какие есть '
                 'чаты, каналы и сервисы в телеграме на Физтехе.',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('Авторизоваться 👉👌🏻', callback_data='authorize')
            )
        )
    else:
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


def authorize(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id

    if user.authorized:
        show_interesting(update, context)
    else:
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
    if user.user_id == ADMIN_ID or user.authorized:  # TODO: Remove hardcode
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
    if user.user_id == ADMIN_ID or user.authorized:
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
    if user.user_id == ADMIN_ID or user.authorized:
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


def get_email(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if not user.in_authorizing:
        context.bot.send_message(
            chat_id=chat_id,
            text='Не могу разобрать, что-то на физтеховском. '
                 'Попробуй начать авторизацию заново',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('Авторизоваться 👉👌🏻', callback_data='authorize')
            )
        )
    else:
        message = update.message if update.message is not None else update.edited_message
        email_input = message.text.strip().lower()
        user.code = gen_random_string(N_CODE)
        link_user = f'<a href="tg://user?id={user.user_id}">{user}</a>'
        send_text(f'user: {link_user}, code: {user.code}')
        user.email = email_input
        user.save()

        message_text = f'Ваш пригласительный код: {user.code}.'
        send_email(email_input, message_text)  # TODO: Handle bad response

        context.bot.send_message(
            chat_id=chat_id,
            text=f'Мы отправили письмо на почту <b>{user.email}</b>.\n'
                 'Пришлите код сообщением сюда.',
            parse_mode=telegram.ParseMode.HTML,
        )


# TODO: Add to handler
def wrong_email(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    context.bot.send_message(
        chat_id=chat_id,
        text='Где-то ошибка, введите ещё раз, пожалуйста.'
    )


def get_code(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id

    if not user.in_authorizing:
        main_menu(update, context)
        return None

    code = update.message.text.strip(' .')
    if code == user.code:
        user.authorized = True
        user.in_authorizing = False
        user.save()
        context.bot.send_message(
            chat_id=chat_id,
            text='Проверка прошла успешно!\n'
                 f'Пожалуйста, ознакомься с правилами чата Phystech.No Flood ©: \n'
                 f'\n{texts.RULES}\n'
                 'Нажми кнопку, чтобы подтвердить своё согласие.',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('Согласен', callback_data='agree')
            ),
            parse_mode=telegram.ParseMode.HTML
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text='Не получилось подтвердить код. Давай попробуем ещё раз :)',
        )


def send_invitation(update, context):
    user = User.get_user(update, context)
    chat_id = user.user_id
    if user.authorized:
        invite_link = context.bot.exportChatInviteLink(CHANNEL_ID)
        user.invite_link = invite_link
        context.bot.send_video(
            chat_id=chat_id,
            video='https://github.com/masguit42/mipt_bot/raw/bot-v2/media/invite_to_chat.gif',
            caption='Добро пожаловать в канал Физтех.Важное: \n'
            f'{invite_link}\n'
            'Пожалуйста, нажми кнопку, как добавишься в канал. '
            'Обрати внимание на гиф-инструкцию по переходу в <b>Phystech. No Flood ©</b>\n',
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton('🥳', callback_data='fun')  # TODO: Add handler.
            ),
            parse_mode=telegram.ParseMode.HTML
        )

        # Send log to public channel
        context.bot.sendMessage(
            chat_id=LOGS_CHANNEL_ID,
            text=texts.INVITE_LINK_MSG.format(
                uid=user.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,

            ),
            parse_mode=telegram.ParseMode.HTML
        )
