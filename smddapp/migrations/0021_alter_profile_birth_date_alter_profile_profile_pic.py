# Generated by Django 4.1.11 on 2024-06-17 11:22

import datetime
from django.db import migrations, models
import smddapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0020_alter_profile_first_name_alter_profile_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 6, 17, 11, 22, 13, 589763, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(blank=True, default='default_profile.jpg', null=True, upload_to=smddapp.models.user_directory_path),
        ),
    ]
