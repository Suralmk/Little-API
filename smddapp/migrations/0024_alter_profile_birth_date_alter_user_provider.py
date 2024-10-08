# Generated by Django 4.1.11 on 2024-09-19 06:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0023_user_provider_alter_profile_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 9, 19, 6, 12, 28, 732593, tzinfo=datetime.timezone.utc), null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='provider',
            field=models.BooleanField(default=False),
        ),
    ]
