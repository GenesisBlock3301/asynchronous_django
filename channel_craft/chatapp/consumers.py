import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from chatapp.models import Room, Message


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None

    # accept connection
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']

        self.accept()

        # send the user list to the newly joined user
        self.send(text_data=json.dumps({
            'type': 'user_list',
            'user': "username"
            # 'users': [user.username for user in self.room.online.all()],
        }))

        # if self.user.is_authenticated:
        #     async_to_sync(self.channel_layer.group_send)(
        #         self.room_group_name,
        #         {
        #             'type': "user_join",
        #             'user': self.user.username
        #         }
        #     )
        #     self.room.online.add(self.user)

        # Join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        # if self.user.is_authenticated:
        #     async_to_sync(self.channel_layer.group_send)(
        #         self.room_group_name,
        #         {
        #             'type': 'user_leave',
        #             'user': self.user.username
        #         }
        #     )

    # Receive message from Websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # if not self.user.is_authenticated:
        #     return
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                # 'user': self.user
                "message": message
            }
        )
        # Message.objects.create(user=self.user, message=message)

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))

    def user_list(self, event):
        self.send(text_data=json.dumps(event))

    # def user_join(self, event):
    #     self.send(text_data=json.dumps(event))
    #
    # def user_leave(self, event):
    #     self.send(text_data=json.dumps(event))
