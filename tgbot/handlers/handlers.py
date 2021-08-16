"""
    This Bot is very cool.
"""

import re
import logging
import telegram

from tgbot.models import User
from tgbot.handlers.logs import send_text
from tgbot.handlers import texts


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
            'обратитесь к модератору @lego1as.',
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


# def reply_start(update, context):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     LOGGER.info(f'Show chats.')
#     update.message.reply_text('Иногда, чтобы начать всё сначала, достаточно нажать /start.',
#                               reply_markup=ReplyKeyboardRemove())
#     return MAIN_MENU


# def wait_for_email(bot, update, user_data):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     text = update.message.text

#     # Check email is in db
#     if (not user_data['email'] is None) and (text != user_data['email']):
#         LOGGER.info(f'Another email exist.')
#         update.message.reply_text(f'Хммм. Есть информация, что ваша почта другая: {user_data["email"]}.\n'
#                                   f'Скорее всего, это связано с тем, что вы вводили её ранее.'
#                                   f'Если вы опечатались или возникла другая ошибка - напишите @lego1as',
#                                   reply_markup=make_kb([['Добавиться в чат'],
#                                                         ['Показать чаты', 'Показать сервисы']]))
#         stage = MAIN_MENU
#     else:
#         LOGGER.info(f'Record email.')
#         if re.match(r'^(\w|\.)+@phystech\.edu$', text):
#             code = gen_random_string(N_CODE)
#             user_data['email'] = text
#             print(code, user_data['email'])

#             concat_string = (str(code)
#                              + str(user_data['first_name'])
#                              + str(user_data['last_name']))
#             user_data['user_hash'] = hash(concat_string)

#             message_text = f'Ваш пригласительный код: {code}.'
#             sent = send_email(user_data['email'], message_text, LOGGER)
#             if sent:
#                 LOGGER.info(f'Successful send message to {user_data["email"]}.')
#             else:
#                 LOGGER.error(f'Cannot send message to {user_data["email"]}.')

#             # TODO: Solve markdown problem
#             update.message.reply_text(
#                 f'Мы отправили письмо на почту **{user_data["email"]}**.\n'
#                 'Пришлите код сообщением сюда.',
#                 parse_mode=ParseMode.MARKDOWN,
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#             stage = WAIT_FOR_EMAIL
#         else:
#             LOGGER.warning(f'Email does not fit pattern.')
#             update.message.reply_text(
#                 'Где-то ошибка, введите ещё раз, пожалуйста.',
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#             stage = ADD_TO_CHAT
#     return stage


# def wait_for_code(bot, update, user_data):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

#     if user_data['attempt'] is None:
#         user_data['attempt'] = 0

#     user_data['attempt'] = user_data['attempt'] + 1
#     LOGGER.info(f'Code reception. Attempt[{user_data["attempt"]}]')

#     if not user_data['attempt'] % 3:
#         LOGGER.warning(f'Wrong code 3 in times in a row. Attempt[{user_data["attempt"]}]')
#         update.message.reply_text('Вы 3 раза ввели неверный код.\n'
#                                   'Пройдите процедуру заново(/start) или обратитесь к модератору @lego1as.',
#                                   reply_markup=make_kb([['Добавиться в чат'],
#                                                         ['Показать чаты', 'Показать сервисы']]),
#                                   )
#         stage = MAIN_MENU
#     else:
#         hash_standard = user_data['user_hash']
#         code = update.message.text
#         concat_string = (str(code)
#                          + str(user_data['first_name'])
#                          + str(user_data['last_name']))
#         hash_current = hash(concat_string)
#         if hash_current == hash_standard:
#             LOGGER.info(f'Successfully approved. Attempt[{user_data["attempt"]}]')
#             user_data['status'] = "approved"
#             update.message.reply_text('Проверка прошла успешно!\n'
#                                       f'Пожалуйста, ознакомьтесь с правилами группы: \n'
#                                       f'\n{RULES}.\n'
#                                       'Напишите "Да", если вы согласны с правилами группы',
#                                       reply_markup=ReplyKeyboardRemove())
#             stage = WAIT_FOR_CODE
#         else:
#             LOGGER.warning(f'Wrong code. Attempt[{user_data["attempt"]}]')
#             attempts_left = 3 - user_data["attempt"] % 3
#             update.message.reply_text('Неверный код. Введите ещё раз.\n'
#                                       f'Осталось попыток: {attempts_left}',
#                                       reply_markup=ReplyKeyboardRemove())
#             stage = WAIT_FOR_EMAIL
#     return stage


# def send_invitation(bot, update, user_data):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')

#     if update.message.text == "Да":
#         LOGGER.info(f'Agree with rules.')
#         invite_link = bot.exportChatInviteLink(CHANNEL_ID)
#         user_data['invite_link'] = invite_link
#         # TODO: Solve markdown problem
#         update.message.reply_text('Добро пожаловать в канал Физтех.Важное: \n'
#                                   f'{invite_link}\n'
#                                   'Внизу с правой стороны будет кнопка для перехода в чат **Phystech. No Flood**\n'
#                                   'Пожалуйста, нажмите кнопку, как добавитесь в чат.',
#                                   reply_markup=make_kb([['Спасибочки']]),
#                                   parse_mode=ParseMode.MARKDOWN)
#         LOGGER.info(f'Link sent.')

#         # Send log to public channel
#         bot.sendMessage(chat_id=LOGS_CHANNEL_ID,
#                         text=INVITE_LINK_MSG.format(
#                             first_name=user_data['first_name'],
#                             last_name=user_data['last_name'],
#                             username=user_data['username'],
#                             uid=user_data['id']))

#         # Record profile
#         profile_db = ProfileDB('data/main.sqlite')
#         if None in user_data.values():
#             LOGGER.error(f'None is in user_data!')
#             bot.sendMessage(chat_id=ADMIN_ID,
#                             text=f'Какая-то проблема с user_data: {user_data}')
#         profile_db.update_profile(user_data)

#         stage = SEND_INVITATION
#     else:
#         LOGGER.warning(f'Misagree with rules.')
#         update.message.reply_text('Осталось только согласиться с правилами. Ну же.')
#         stage = WAIT_FOR_CODE
#     return stage


# def help_menu(bot, update):
#     LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     LOGGER.info(f'Use help menu.')
#     update.message.reply_text("По всем возникшим вопросам и предложениям писать @lego1as",
#                               reply_markup=make_kb([['Добавиться в чат'],
#                                                     ['Показать чаты', 'Показать сервисы']]))
#     return MAIN_MENU


# def error(bot, update, error):
#     if not update is None:
#         LOGGER = logging.getLogger(f'user#{update.message.from_user.id}')
#     else:
#         LOGGER = logging.getLogger('root')
#     LOGGER.error(f'Update "{update}" caused error "{error}"')
