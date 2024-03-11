# Generated by Django 4.1.11 on 2023-12-08 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smddapp', '0006_alter_follow_follow_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='follow_user',
        ),
        migrations.AddField(
            model_name='profile',
            name='follow',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='follow', to='smddapp.follow'),
        ),
    ]