# Generated by Django 4.1.11 on 2023-12-21 09:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smddpost', '0010_comment_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, default='', related_name='like_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
