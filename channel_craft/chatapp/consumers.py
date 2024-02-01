import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = None
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None

    # accept connection
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope['user']
        # self.username = await database_sync_to_async(self.get_name)()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # send the user list to the newly joined user, it is worked after successfully connect.
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'user_list', 'users': User.objects.all()}
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from Websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        # send message to websocket
        await self.send(text_data=json.dumps({"message": message}))

    async def user_list(self, event):
        await self.send(text_data=json.dumps(event))

    def get_name(self):
        return User.objects.all()[0].username

    # def user_join(self, event):
    #     self.send(text_data=json.dumps(event))
    #
    # def user_leave(self, event):
    #     self.send(text_data=json.dumps(event))
