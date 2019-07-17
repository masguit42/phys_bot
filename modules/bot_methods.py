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
import logging
import re

from telegram import (
    ReplyKeyboardRemove,
    ParseMode, Chat, TelegramError)
from telegram.ext import ConversationHandler

from .constants import (
    MAIN_MENU, ADD_TO_CHAT,
    WAIT_FOR_EMAIL, WAIT_FOR_CODE,
    SEND_INVITATION,
    ADMIN_ID, LOGS_CHANNEL_ID, MAIN_CHAT_ID,
    CHANNEL_ID, CHATS, SERVICES, RULES,
    INVITE_LINK_MSG,
    N_CODE,
    SMTP_SINGIN, LOG_FILE)
from .utilities import (
    send_email,
    make_kb, gen_random_string,
    get_smtp_server, init_user_data)
from .db_bot import ProfileDB

SERVER = get_smtp_server(SMTP_SINGIN)

# Enable logging
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main_menu(bot, update, user_data):

    # Check chat is private
    if update.message.chat.type != 'private':
        print(update.message.from_user.id)
        update.message.reply_text(
            'Этот бот не может работать в этом чяте.',
            reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # User data primary set up
    user_data['id'] = update.message.from_user.id
    user_data = init_user_data(user_data)

    # Check profile is in db
    profile_db = ProfileDB('data/main.sqlite')
    existed_profile = profile_db.get_by_id(user_data['id'])
    # Fill user_data if profile exists
    if not existed_profile is None:
        # TODO: log INFO Profile _id_ in db already
        for key, value in existed_profile.to_dict().items():
            user_data[key] = value
    else:
        # TODO: log INFO Profile _id_ not in db yet
        pass

    for key in ['first_name', 'last_name', 'username']:
        user_data[key] = (update.message.from_user[key]
                          if user_data[key] is None else user_data[key])

    update.message.reply_text(
        f'Привет, {user_data["first_name"]}. '
        f'Этот бот поможет вам добавиться в общий чат физтехов, '
        f'даст информацию о том, какие есть тематические '
        f'чаты и каналы на Физтехе.',
        reply_markup=make_kb([['Добавиться в чат'],
                              ['Показать чаты', 'Показать сервисы']]),
    )
    return MAIN_MENU


def add_to_chat(bot, update, user_data):

    in_chat = False
    try:
        bot.get_chat_member(chat_id=MAIN_CHAT_ID,
                            user_id=update.message.from_user.id,
                            timeout=5)
    except TelegramError:
        pass
    except Exception as problem:
        # TODO: log ERROR : _problem_ with user _id_
        print('problem in add_to_chat')
    else:
        in_chat = True

    # TODO: Remove debug command
    if False:
    # if in_chat or user_data['status'] == 'approved':
        update.message.reply_text(
            'Вы уже были добавлены в чат. \n'
            'В случае возникновения проблем, '
            'обратитесь к модератору @lego1as.',
            reply_markup=make_kb([['Показать чаты', 'Показать сервисы']])
        )
        return MAIN_MENU
    else:
        update.message.reply_text(
            'Чтобы добавить вас в чат, необходимо удостовериться, что вы с МФТИ. '
            'Напишите свою почту на домене **phystech.edu** '
            'и мы вышлем на неё секретный код. '
            'После этого, напишите сюда код с электронной почты '
            'и вам дадут ссылку на добавление в чат.',
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ADD_TO_CHAT


def show_chats(bot, update):

    update.message.reply_text(CHATS,
                              reply_markup=make_kb([['Добавиться в чат', 'Показать сервисы']]))
    return MAIN_MENU


def show_services(bot, update):

    update.message.reply_text(SERVICES,
                              reply_markup=make_kb([['Добавиться в чат', 'Показать чаты']]))
    return MAIN_MENU


def wait_for_email(bot, update, user_data):
    text = update.message.text
    # Check email is in db
    if (not user_data['email'] is None) and (text != user_data['email']):
        update.message.reply_text(f'Хммм. Есть информация, что ваша почта другая: {user_data["email"]}'
                                  f'Скорее всего, это связано с тем, что вы вводили её ранее.'
                                  f'Если вы опечатались или возникла другая ошибка - напишите @lego1as',
                                  reply_markup=make_kb([['Показать чаты', 'Показать сервисы']]))
        return MAIN_MENU
    else:
        # TODO: log INFO new email added for _id_

        if re.match(r'^(\w|\.)+@phystech\.edu$', text):
            code = gen_random_string(N_CODE)
            user_data['email'] = text
            concat_string = code + user_data['first_name'] + user_data['last_name']
            user_data['user_hash'] = hash(concat_string)
            message_text = f'Your invitation code is {code}.'
            send_email(SERVER, user_data['email'], message_text)
            # TODO: Solve markdown problem
            update.message.reply_text(
                f'Мы отправили письмо на почту **{user_data["email"]}**.\n'
                'Пришлите код сообщением сюда.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardRemove(),
            )
            return WAIT_FOR_EMAIL
        else:
            update.message.reply_text(
                'Где-то ошибка, введите ещё раз, пожалуйста.',
                reply_markup=ReplyKeyboardRemove(),
            )
            return ADD_TO_CHAT


def wait_for_code(bot, update, user_data):

    if user_data['attempt'] is None:
        user_data['attempt'] = 0

    user_data['attempt'] = user_data['attempt'] + 1
    if not user_data['attempt'] % 3:
        update.message.reply_text('Вы 3 раза ввели неверный код.\n'
                                  'Пройдите процедуру заново(/start) или обратитесь к модератору @lego1as.')
        return MAIN_MENU

    hash_standard = user_data['user_hash']
    code = update.message.text
    concat_string = code + user_data['first_name'] + user_data['last_name']
    hash_current = hash(concat_string)
    if hash_current == hash_standard:
        user_data['status'] = "approved"
        update.message.reply_text('Проверка прошла успешно!\n'
                                  f'Пожалуйста, ознакомьтесь с правилами группы: \n'
                                  f'\n{RULES}.\n'
                                  'Напишите "Да", если вы согласны с правилами группы',
                                  reply_markup=ReplyKeyboardRemove())
        return WAIT_FOR_CODE
    else:
        attempts_left = 3 - user_data["attempt"] % 3
        update.message.reply_text('Неверный код. Введите ещё раз.\n'
                                  f'Осталось попыток: {attempts_left}',
                                  reply_markup=ReplyKeyboardRemove())
        return WAIT_FOR_EMAIL


def send_invitation(bot, update, user_data):

    if update.message.text == "Да":
        invite_link = bot.exportChatInviteLink(CHANNEL_ID)
        user_data['invite_link'] = invite_link
        # TODO: Solve markdown problem
        update.message.reply_text('Добро пожаловать в канал Физтех.Важное:\n'
                                  f'{invite_link}\n'
                                  'Внизу с правой стороны будет кнопка для перехода в чат **Phystech. No Flood**\n',
                                  reply_markup=make_kb([['Спасибо']]),
                                  parse_mode=ParseMode.MARKDOWN)

        profile_db = ProfileDB('data/main.sqlite')
        if None in user_data.values():
            bot.sendMessage(chat_id=ADMIN_ID,
                            text=f'Какая-то проблема с user_data: {user_data}')

        profile_db.update_profile(user_data)

        return SEND_INVITATION
    else:
        update.message.reply_text('Осталось только согласиться с правилами. Ну же.')
        return WAIT_FOR_CODE


def done(bot, update, user_data):
    bot.sendMessage(chat_id=LOGS_CHANNEL_ID,
                    text=INVITE_LINK_MSG.format(
                        username=user_data['username'],
                        uid=user_data['id']))
    # TODO: check user is in chat
    bot.sendMessage(chat_id=ADMIN_ID,
                    text='New user. Revoke link please.')

    return ConversationHandler.END


def help_menu(bot, update):
    update.message.reply_text("Suk, nu privet!")


def error(bot, update, error):
    logger.warning(f'Update "{update}" caused error "{error}"')
