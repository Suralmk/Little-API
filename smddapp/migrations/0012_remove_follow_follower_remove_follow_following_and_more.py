# Generated by Django 4.1.11 on 2023-12-08 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0011_remove_profile_follow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='follower',
        ),
        migrations.RemoveField(
            model_name='follow',
            name='following',
        ),
        migrations.AddField(
            model_name='follow',
            name='name',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
