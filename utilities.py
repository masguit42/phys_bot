import random
import string
from telegram import ReplyKeyboardMarkup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def encode_lp(file):
    with open(file, 'r') as f:
        login, pswd, *_ = f.read().split('\n')
        login = [int(c)-1 for c in login.split(' ')]
        pswd = [int(c)+1 for c in pswd.split(' ')]

    login = bytearray(login).decode('utf-8')
    pswd = bytearray(pswd).decode('utf-8')

    return login, pswd


def gen_random_string(n):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def make_kb(keys, one_time_keyboard=True):
    return ReplyKeyboardMarkup(keys, resize_keyboard=True, one_time_keyboard=one_time_keyboard)


def send_email(email, message_text):
    fromaddr = "akostin@phystech.edu"
    toaddr = email
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Phystech identification"
    body = message_text

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(*encode_lp('singin.txt'))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
