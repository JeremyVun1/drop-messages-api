from django.urls import path
from .consumers import MessagesConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', MessagesConsumer),
]