# Generated by Django 3.1.3 on 2021-08-29 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_auto_20210816_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]