from django.contrib.auth import get_user_model
from rest_framework import serializers
from . models import Message

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source = "sender.get_full_name")
    reciver = serializers.CharField(source = "reciver.get_full_name")
    timestamp = serializers.DateTimeField()
    class Meta:
        model = Message
        fields = ["sender", "reciver", "message", "timestamp"]

class MessageSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["reciver", "message"]

        def send_message(self, sender, clean_data):
            message = Message.objects.create(sender=sender, reciver=clean_data['reciver'], message=clean_data['message'])
            message.save()
            return message



