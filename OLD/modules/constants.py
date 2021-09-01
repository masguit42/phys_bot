USER_DATA_KEYS = (
    'id',
    'first_name',
    'last_name',
    'email',
    'status',
    'user_hash',
    'attempt',
    'invite_link',
    'username')

ALLOWED_STATUSES = ("approved", "not_approved",
                    "administrator", "creator", "kicked",
                    "left", "member", "restricted")

RESTRICTED = 'restricted'

RULES = '''🚩 Если собираетесь вывесить объявление о работе, поставьте тэг #_job и вилку
🚩 Запрещено вывешивать объявления до подтверждения статуса Физтех
🚩 Запрещено обсуждение любой политической позиции
🚩 Запрещены прямые оскорбления
🚩 Сообщения с матами чистятся без разбора (корни на х,п,е,б)
🚩 Запрещено добавлять нефизтехов, любые объявления от нефизтехов передавать через @lego1as или @okhlopkov
🚩 Чтобы добавить кого-нибудь в чат, пишите @lego1as, @caffeinum, @ivanychev
'''

(MAIN_MENU,
 ADD_TO_CHAT,
 WAIT_FOR_EMAIL, WAIT_FOR_CODE,
 SEND_INVITATION, *_) = range(100)

ADMIN_ID = 143871296 # realkostin
LOGS_CHANNEL_ID = -1001391309276  # No Flood. Logs
CHANNEL_ID = -1001110086957  # Phystech.Важное
MAIN_CHAT_ID = -1001092483713  # Phystech. No Flood

N_CODE = 6
N_MINUTES_PER_INVITE = 2

INVITE_LINK_MSG = """
#NEW_INVITATION\n
• Channel: Phystech.Важное [#chat1001092483713]\n
• User: {first_name} {last_name} [@{username}] [#id{uid}]
"""

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CHATS = 'content/chats.txt'
SERVICES = 'content/services.txt'

SMTP_SINGIN = 'data/singin.txt'
BOT_TOKEN = 'data/token.txt'
LOG_FILE = 'data/logs.txt'

