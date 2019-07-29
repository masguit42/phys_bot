# import ssl
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string
from time import sleep

from telegram import ReplyKeyboardMarkup, TelegramError

from .constants import (
    USER_DATA_KEYS, MAIN_CHAT_ID,
    SMTP_SERVER, SMTP_PORT,
    N_MINUTES_PER_INVITE, SMTP_SINGIN)


def init_user_data(primary_user_data):

    for key in USER_DATA_KEYS:
        if key not in primary_user_data.keys():
            primary_user_data[key] = None
    primary_user_data['status'] = "not_approved"
    return primary_user_data


def encode_lp(file):
    with open(file, 'r') as f:
        login, pswd, *_ = f.read().split('\n')
        login = [int(c)-10 for c in login.split(' ')]
        pswd = [int(c)+7 for c in pswd.split(' ')]

    login = bytearray(login).decode('utf-8')
    pswd = bytearray(pswd).decode('utf-8')

    return login, pswd


def gen_random_string(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def make_kb(keys, one_time_keyboard=True):
    return ReplyKeyboardMarkup(keys,
                               resize_keyboard=True,
                               one_time_keyboard=one_time_keyboard)


def get_smtp_server(server=None):
    sender_email, password = encode_lp(SMTP_SINGIN)

    # context = ssl.create_default_context()
    if server is None:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    else:
        server.connect(SMTP_SERVER, SMTP_PORT)
    server.ehlo()  # Can be omitted
    server.starttls()
    # server.starttls(context=context)
    server.ehlo()  # Can be omitted
    code_response, _ = server.login(sender_email, password)

    return server, code_response


def send_email(receiver_email, message_text, logger):
    for i in range(5):
        server, code_response = get_smtp_server()
        if code_response == 235:
            break
        else:
            logger.warn(f'Cannot login to smtp server. Code: {code_response}')
            sleep(30)
    else:
        logger.error(f'Cannot login for send message to {receiver_email}')

    sent = False

    msg = MIMEMultipart()
    msg['From'] = server.user
    msg['To'] = receiver_email
    msg['Subject'] = "Chat Invitation"
    msg.attach(MIMEText(message_text, 'plain'))
    for i in range(5):
        try:
            server.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            server = get_smtp_server(server=server)
        except Exception as problem:
            logger.error(f'Problem with update {problem}')
        else:
            sent = True
            break
    server.quit()

    del msg
    return sent


def check_user_in_chat(bot, update, logger):
    in_chat = False
    try:
        bot.get_chat_member(chat_id=MAIN_CHAT_ID,
                            user_id=update.message.from_user.id,
                            timeout=5)
    except TelegramError:
        pass
    except Exception as problem:
        logger.error(f'Exception in check_in_chat {problem}')
    else:
        in_chat = True

    return in_chat


def check_n_wait_for_user_in_chat(bot, update, in_chat, logger):
    for i in range(N_MINUTES_PER_INVITE):
        if not in_chat:
            in_chat = check_user_in_chat(bot, update, logger)
            sleep(60)
        else:
            break
    return in_chat
