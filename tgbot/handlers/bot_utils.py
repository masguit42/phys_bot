import random
import string
from time import sleep

import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telegram
from telegram.error import BadRequest
from telegram import TelegramError
from tgbot.handlers.bot_constants import (
    TELEGRAM_TOKEN, N_MINUTES_PER_INVITE,
    EMAIL_BOT, PASSWORD_EMAIL_BOT, MAIN_CHAT_ID,
    SMTP_SERVER, SMTP_PORT,
)

DEBUG = True  # TODO: Change debug to False.


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


def get_smtp_server(server=None):
    if server is None:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    else:
        server.connect(SMTP_SERVER, SMTP_PORT)

    context = ssl.create_default_context()
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    code_response, _ = server.login(EMAIL_BOT, PASSWORD_EMAIL_BOT)
    return server, code_response


def send_email(receiver_email, message_text):
    for i in range(5):
        server, code_response = get_smtp_server()
        if code_response == 235:
            break
        else:
            sleep(30)  # TODO: Handle time dilation.
    else:
        pass

    msg = MIMEMultipart()
    msg['From'] = server.user
    msg['To'] = receiver_email
    msg['Subject'] = "Chat Invitation"
    msg.attach(MIMEText(message_text, 'plain'))
    sent = False
    for i in range(5):
        try:
            server.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            server = get_smtp_server(server=server)
        except Exception as problem:
            pass
            # logger.error(f'Problem with update {problem}')
        else:
            sent = True
            break
    server.quit()

    del msg
    return sent


def check_user_in_chat(bot, update, logger):
    in_chat = True
    try:
        chat_member = bot.get_chat_member(
            chat_id=MAIN_CHAT_ID,
            user_id=update.message.from_user.id,
            timeout=5)
        if chat_member['status'] == 'left':
            in_chat = False
    except TelegramError:
        in_chat = False
    except Exception as problem:
        logger.error(f'Exception in check_in_chat {problem}')

    return in_chat


def check_n_wait_for_user_in_chat(bot, update, in_chat, logger):
    for i in range(N_MINUTES_PER_INVITE):
        if not in_chat:
            in_chat = check_user_in_chat(bot, update, logger)
            sleep(60)
        else:
            break
    return in_chat
