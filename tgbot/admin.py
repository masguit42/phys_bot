import random
from django.contrib import admin
from django.http import HttpResponseRedirect
from tgbot.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username',
        'first_name', 'last_name',
        'language_code', 'code', 'email',
        'created_at', 'updated_at', "is_blocked_bot",
    ]
    list_filter = ["is_blocked_bot", "is_admin"]
    search_fields = ('username', 'user_id')
