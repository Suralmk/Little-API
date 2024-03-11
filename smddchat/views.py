from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status, generics

from . serializers import *
from . models import Message
from smddapp.models import Profile
from django.contrib.auth import get_user_model
from django.db.models import Q
User= get_user_model()

class MessageView(APIView):
    def get (self, request, username):
        user = Profile.objects.filter(username__iexact=username).first()
        active_messages = Message.objects.filter(Q(reciver=user.id) | Q(sender=user.id)  ).all()
        serializer = MessageSerializer(active_messages, many=True)
        return Response (  serializer.data)
    
class MessageSendView(generics.CreateAPIView):
    serializer_class = MessageSendSerializer
    
    def post(self, request, username):
        user = Profile.objects.filter(username__iexact=username).first()
        sender = user.id
        clean_data = request.data
        serializer = self.get_serializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_message(sender,clean_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error" : "couldn't send message"}, status=status.HTTP_201_CREATED)
        