"""
    This Bot is very cool.
"""
import logging
import re

from telegram import (
    ReplyKeyboardRemove,
    ParseMode)  # Chat, TelegramError)
from telegram.ext import ConversationHandler

from .constants import (
    MAIN_MENU, ADD_TO_CHAT,
    WAIT_FOR_EMAIL, WAIT_FOR_CODE,
    SEND_INVITATION,
    ADMIN_ID, LOGS_CHANNEL_ID,  # MAIN_CHAT_ID,
    CHANNEL_ID, CHATS, SERVICES, RULES,
    INVITE_LINK_MSG,
    N_CODE,  # N_MINUTES_PER_INVITE,
    # SMTP_SINGIN,
    LOG_FILE)
from .utilities import (
    send_email, check_user_in_chat,
    make_kb, gen_random_string,
    # get_smtp_server,
    init_user_data,
    check_n_wait_for_user_in_chat)
from .db_bot import ProfileDB

# Enable logging
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logger = logging.getLogger(__name__)
LOGGER = logging.getLogger('root')


def main_menu(bot, update, user_data):
    LOGGER = logging.getLogger('root')
    # Check chat is private
    if update.message.chat.type != 'private':
        print(f'User: {update.message.from_user.id}, Chat: {update.message.chat.id}')
        update.message.reply_text(
            'Этот бот не может работать в этом чяте.',
            reply_markup=ReplyKeyboardRemove())
        LOGGER.info(f'Someone[id#{update.message.from_user.id}] starts bot in not private chat.')
        return ConversationHandler.END

    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

    # User data primary set up
    user_data['id'] = update.message.from_user.id
    user_data = init_user_data(user_data)

    # Check profile is in db
    profile_db = ProfileDB('data/main.sqlite')
    existed_profile = profile_db.get_by_id(user_data['id'])
    # Fill user_data if profile exists
    if not existed_profile is None:
        LOGGER.info(f'User exists in db.')
        for key, value in existed_profile.to_dict().items():
            user_data[key] = value
    else:
        LOGGER.info(f'User not exist in db.')
        pass

    for key in ['first_name', 'last_name', 'username']:
        user_data[key] = (update.message.from_user[key]
                          if user_data[key] is None else user_data[key])

    in_chat = check_user_in_chat(bot, update, LOGGER)
    if update.message.text == 'Спасибочки':

        in_chat = check_n_wait_for_user_in_chat(bot, update, in_chat, LOGGER)

        if in_chat:
            bot.sendMessage(chat_id=ADMIN_ID,
                            text='New user. Revoke link please.')
            LOGGER.info(f'Link pseudo-revoking.')
            update.message.reply_text(
                'Круто, теперь ты с нами!',
                reply_markup=make_kb([['Показать чаты', 'Показать сервисы']]))
        else:
            update.message.reply_text(
                'Рекомендуем пройти процедуру получения ссылки заново.\n'
                'В случае возникновения проблем, '
                'обратитесь к модератору @lego1as.',
                reply_markup=make_kb([['Добавиться в чат'],
                                      ['Показать чаты', 'Показать сервисы']])
            )
            LOGGER.warning(f'Unhandled behaviour in modules.bot_methods.main_menu.')
    else:
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
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    in_chat = check_user_in_chat(bot, update, LOGGER)

    if in_chat or user_data['status'] == 'approved':
        LOGGER.info(f'User already in chat or approved.')
        update.message.reply_text(
            'Вы уже были добавлены в чат. \n'
            'В случае возникновения проблем, '
            'обратитесь к модератору @lego1as.',
            reply_markup=make_kb([['Показать чаты', 'Показать сервисы']])
        )
        stage = MAIN_MENU
    else:
        update.message.reply_text(
            'Чтобы добавить вас в чат, необходимо удостовериться, что вы из МФТИ. '
            'Напишите свою почту на домене **phystech.edu** '
            'и мы вышлем на неё секретный код. '
            'После этого, напишите сюда код с электронной почты '
            'и вам дадут ссылку на добавление в чат.',
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )
        stage = ADD_TO_CHAT
    return stage


def show_chats(bot, update):
    with open(CHATS) as f:
        chats = f.read()
    update.message.reply_text(chats,
                              reply_markup=make_kb([['Добавиться в чат',
                                                     'Показать сервисы']]))
    return MAIN_MENU


def show_services(bot, update):
    with open(SERVICES) as f:
        services = f.read()
    update.message.reply_text(services,
                              parse_mode=ParseMode.HTML,
                              reply_markup=make_kb([['Добавиться в чат',
                                                     'Показать чаты']]))
    return MAIN_MENU


def reply_start(bot, update):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    LOGGER.info(f'Show chats.')
    update.message.reply_text('Иногда, чтобы начать всё сначала, достаточно нажать /start.',
                              reply_markup=ReplyKeyboardRemove())
    return MAIN_MENU


def wait_for_email(bot, update, user_data):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    text = update.message.text

    # Check email is in db
    if (not user_data['email'] is None) and (text != user_data['email']):
        LOGGER.info(f'Another email exist.')
        update.message.reply_text(f'Хммм. Есть информация, что ваша почта другая: {user_data["email"]}.\n'
                                  f'Скорее всего, это связано с тем, что вы вводили её ранее.'
                                  f'Если вы опечатались или возникла другая ошибка - напишите @lego1as',
                                  reply_markup=make_kb([['Добавиться в чат'],
                                                        ['Показать чаты', 'Показать сервисы']]))
        stage = MAIN_MENU
    else:
        LOGGER.info(f'Record email.')
        if re.match(r'^(\w|\.)+@phystech\.edu$', text):
            code = gen_random_string(N_CODE)
            user_data['email'] = text
            print(code, user_data['email'])

            concat_string = (str(code)
                             + str(user_data['first_name'])
                             + str(user_data['last_name']))
            user_data['user_hash'] = hash(concat_string)

            message_text = f'Ваш пригласительный код: {code}.'
            sent = send_email(user_data['email'], message_text, LOGGER)
            if sent:
                LOGGER.info(f'Successful send message to {user_data["email"]}.')
            else:
                LOGGER.error(f'Cannot send message to {user_data["email"]}.')

            # TODO: Solve markdown problem
            update.message.reply_text(
                f'Мы отправили письмо на почту **{user_data["email"]}**.\n'
                'Пришлите код сообщением сюда.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ReplyKeyboardRemove(),
            )
            stage = WAIT_FOR_EMAIL
        else:
            LOGGER.warning(f'Email does not fit pattern.')
            update.message.reply_text(
                'Где-то ошибка, введите ещё раз, пожалуйста.',
                reply_markup=ReplyKeyboardRemove(),
            )
            stage = ADD_TO_CHAT
    return stage


def wait_for_code(bot, update, user_data):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

    if user_data['attempt'] is None:
        user_data['attempt'] = 0

    user_data['attempt'] = user_data['attempt'] + 1
    LOGGER.info(f'Code reception. Attempt[{user_data["attempt"]}]')

    if not user_data['attempt'] % 3:
        LOGGER.warning(f'Wrong code 3 in times in a row. Attempt[{user_data["attempt"]}]')
        update.message.reply_text('Вы 3 раза ввели неверный код.\n'
                                  'Пройдите процедуру заново(/start) или обратитесь к модератору @lego1as.',
                                  reply_markup=make_kb([['Добавиться в чат'],
                                                        ['Показать чаты', 'Показать сервисы']]),
                                  )
        stage = MAIN_MENU
    else:
        hash_standard = user_data['user_hash']
        code = update.message.text
        concat_string = (str(code)
                         + str(user_data['first_name'])
                         + str(user_data['last_name']))
        hash_current = hash(concat_string)
        if hash_current == hash_standard:
            LOGGER.info(f'Successfully approved. Attempt[{user_data["attempt"]}]')
            user_data['status'] = "approved"
            update.message.reply_text('Проверка прошла успешно!\n'
                                      f'Пожалуйста, ознакомьтесь с правилами группы: \n'
                                      f'\n{RULES}.\n'
                                      'Напишите "Да", если вы согласны с правилами группы',
                                      reply_markup=ReplyKeyboardRemove())
            stage = WAIT_FOR_CODE
        else:
            LOGGER.warning(f'Wrong code. Attempt[{user_data["attempt"]}]')
            attempts_left = 3 - user_data["attempt"] % 3
            update.message.reply_text('Неверный код. Введите ещё раз.\n'
                                      f'Осталось попыток: {attempts_left}',
                                      reply_markup=ReplyKeyboardRemove())
            stage = WAIT_FOR_EMAIL
    return stage


def send_invitation(bot, update, user_data):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

    if update.message.text == "Да":
        LOGGER.info(f'Agree with rules.')
        invite_link = bot.exportChatInviteLink(CHANNEL_ID)
        user_data['invite_link'] = invite_link
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
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            username=user_data['username'],
                            uid=user_data['id']))

        # Record profile
        profile_db = ProfileDB('data/main.sqlite')
        if None in user_data.values():
            LOGGER.error(f'None is in user_data!')
            bot.sendMessage(chat_id=ADMIN_ID,
                            text=f'Какая-то проблема с user_data: {user_data}')
        profile_db.update_profile(user_data)

        stage = SEND_INVITATION
    else:
        LOGGER.warning(f'Misagree with rules.')
        update.message.reply_text('Осталось только согласиться с правилами. Ну же.')
        stage = WAIT_FOR_CODE
    return stage


def done(bot, update):
    return ConversationHandler.END


def help_menu(bot, update):
    LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    LOGGER.info(f'Use help menu.')
    update.message.reply_text("По всем возникшим вопросам и предложениям писать @lego1as",
                              reply_markup=make_kb([['Добавиться в чат'],
                                                    ['Показать чаты', 'Показать сервисы']]))
    return MAIN_MENU


def error(bot, update, error):
    if not update is None:
        LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
    else:
        LOGGER = logging.getLogger('root')
    LOGGER.error(f'Update "{update}" caused error "{error}"')
