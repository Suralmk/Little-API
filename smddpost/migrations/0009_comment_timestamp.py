# Generated by Django 4.1.11 on 2023-12-20 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smddpost', '0008_alter_post_caption'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]