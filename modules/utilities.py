import ssl
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string

from telegram import ReplyKeyboardMarkup

from modules.constants import USER_DATA_KEYS


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


def get_smtp_server(file):

    sender_email, password = encode_lp(file)
    smtp_server = "smtp.gmail.com"

    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, 587)
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)

    return server


def send_email(server, receiver_email, message_text):
    # TODO: Add title of message.
    msg = MIMEMultipart()

    msg['From'] = server.user
    msg['To'] = receiver_email
    msg['Subject'] = "Chat Invitation"
    msg.attach(MIMEText(message_text, 'plain'))

    # server.sendmail(server.user, receiver_email, msg)
    server.send_message(msg)

    del msg
