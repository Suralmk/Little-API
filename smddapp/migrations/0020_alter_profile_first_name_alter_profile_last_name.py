# Generated by Django 4.1.11 on 2023-12-13 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0019_alter_profile_first_name_alter_profile_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(blank=True, default='Unknown', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(blank=True, default='Name', max_length=100, null=True),
        ),
    ]