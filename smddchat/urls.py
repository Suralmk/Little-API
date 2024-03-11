
from django.urls import path
from . views import *
urlpatterns = [
    path('', MessageView.as_view()),
    path('new/', MessageSendView.as_view()),
]