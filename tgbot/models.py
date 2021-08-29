import telegram

from django.db import models
from miptbot.settings import TELEGRAM_TOKEN
from tgbot import utils

nb = dict(null=True, blank=True)


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    email = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb) 

    is_blocked_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    code = models.PositiveSmallIntegerField(**nb)
    status = models.CharField(max_length=32, **nb)
    is_in_chat = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'@{self.username}' if self.username else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update, context):
        """ python-telegram-bot's Update, Context --> User instance """
        data = utils.extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:  # don't change deep_link for already created users
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update, context):
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string):
        """ Search user in DB, return User or None if not found """
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    def send_message(
            self,
            text,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=None,
            reply_to_message_id=None,
            disable_web_page_preview=None,
    ):  # TODO: refactor?
        try:
            bot = telegram.Bot(TELEGRAM_TOKEN)
            m = bot.send_message(
                chat_id=self.user_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
                disable_web_page_preview=disable_web_page_preview,
            )
        except telegram.error.Unauthorized:
            print(f"Can't send message to {self}. Reason: Bot was stopped.")
            self.is_blocked_bot = True
            success = False
        except Exception as e:
            print(f"Can't send message to {self}. Reason: {e}")
            success = False
        else:
            success = True
            self.is_blocked_bot = False
        finally:
            self.save()
        return success
