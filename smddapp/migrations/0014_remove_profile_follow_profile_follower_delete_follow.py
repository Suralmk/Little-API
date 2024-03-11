# Generated by Django 4.1.11 on 2023-12-08 12:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0013_remove_follow_name_follow_follower_follow_following_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='follow',
        ),
        migrations.AddField(
            model_name='profile',
            name='follower',
            field=models.ManyToManyField(default='', related_name='following', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Follow',
        ),
    ]