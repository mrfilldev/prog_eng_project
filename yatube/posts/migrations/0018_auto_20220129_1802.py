# Generated by Django 2.2.16 on 2022-01-29 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
