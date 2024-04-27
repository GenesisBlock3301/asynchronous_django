# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notification_send/$', consumers.NotificationConsumer.as_asgi())
]
