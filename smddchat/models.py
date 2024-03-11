from django.db import models
from smddapp.models import User
# Create your models here.


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="message_sender", on_delete=models.CASCADE, null=False)
    reciver = models.ForeignKey(User, related_name="message_reciver", on_delete=models.CASCADE, null=False)
    message = models.TextField( max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)