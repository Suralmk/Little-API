# Generated by Django 4.1.11 on 2023-12-08 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0004_follow_user_delete_stream'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='user',
            new_name='follow_user',
        ),
    ]
