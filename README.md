# Telegram bot for Phystech.No Flood chat

This bot authorizes users before they can access student chat.

## How to run

Create .env in the root folder (with your own values):

```bash
TELEGRAM_TOKEN="1111111:AAAAAAAAAAAAAAAAAA"
ADMIN_ID=111111111
LOGS_CHANNEL_ID="-1001111111111"
TELEGRAM_LOGS_CHAT_ID="-1001111111111"
CHANNEL_ID="-1001111111111"
MAIN_CHAT_ID="-1001111111111"

EMAIL_BOT="aaaaaaaaa@phystech.edu"
PASSWORD_EMAIL_BOT="1111111111"

DJANGO_DEBUG=True
N_CODE=6 # needs to be 6 because it is hardcoded in regexp for some reason

DATABASE_URL=sqlite:///db.sqlite3
```

Run with docker-compose:

```bash
docker compose up
```

Run without docker:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --run-syncdb # creates db
python run_pooling.py                 # starts bot
```