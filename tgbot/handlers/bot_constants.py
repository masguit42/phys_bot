import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')  # \r\e\a\l\k\o\s\t\i\n\
LOGS_CHANNEL_ID = os.getenv('LOGS_CHANNEL_ID')  # \N\o\ \F\l\o\o\d\.\ \L\o\g\s\
CHANNEL_ID = os.getenv('CHANNEL_ID')  # \P\h\ys\t\e\c\h\.\В\а\ж\н\о\е\
MAIN_CHAT_ID = os.getenv('MAIN_CHAT_ID')
N_CODE = int(os.getenv('N_CODE'))
EMAIL_BOT = os.getenv("EMAIL_BOT")
PASSWORD_EMAIL_BOT = os.getenv("PASSWORD_EMAIL_BOT")

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

N_MINUTES_PER_INVITE = 2
