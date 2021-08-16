import html
import logging
import traceback

import telegram
from telegram import Update

from tgbot.models import User
from miptbot.settings import TELEGRAM_LOGS_CHAT_ID


def send_stacktrace_to_tg_chat(update, context):
    u, _ = User.get_user_and_created(update, context)

    logging.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        # f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        # '</pre>\n\n'
        # f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        # f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )
    
    context.bot.send_message(
        text="😔 Something broke inside the bot. It is because we are constantly improving our service but sometimes we might forget to test some basic stuff.\nPlease give us couple hours too fix it. We already received all the details.\n\nReturn to /menu",
        chat_id=u.user_id,
    )
    error_text_to_send = f"⚠️⚠️⚠️ for {u.tg_str()}:\n{message}"[:4090]
    return context.bot.send_message(
        chat_id=TELEGRAM_LOGS_CHAT_ID,  # @okhlopkov
        text=error_text_to_send,
        parse_mode=telegram.ParseMode.HTML,
    )