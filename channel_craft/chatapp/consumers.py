import json, subprocess, logging
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
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f"chat_{self.room_name}"
            self.user = self.scope['user']
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            previous_messages = ["message1", "message2", "message3"]

            for message in previous_messages:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "chat_message", "message": message}
                )

            users = await self.get_users()
            logging.info("Connected successfully")
            # send the user list to the newly joined user, it is worked after successfully connect.
            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'user_list', 'users': users}
            )
        except Exception as e:
            logging.error(e)
            pass

    async def disconnect(self, close_code):
        pass

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

        # Use sync_to_async decorator to make synchronous database query asynchronous
    @database_sync_to_async
    def get_users(self):
        users = User.objects.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return user_list


class CommandLineConsumer(AsyncWebsocketConsumer):

    async def execute_shell_command(self, command, password=None, input_data=None):
        if password:
            command = f'echo "{password}" | sudo -S {command}'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True)
        while True:
            stdout = process.stdout.readline().strip()
            stderr = process.stderr.readline().strip()
            if stdout:
                # print("output:", stdout)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "chat_message", "message": stdout}
                )
            if stderr:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "chat_message", "message": stderr}
                )

            if not stdout and not stderr:
                break

    def __init__(self):
        self.room_group_name = "command-line"
        super().__init__()

    async def connect(self):
        await self.channel_layer.group_add("command-line", self.channel_name)
        await self.accept()

        await self.execute_shell_command("sudo apt -y upgrade", "bs23")

    async def disconnect(self, close_code):
        await self.close()

    # Receive message from Websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        previous_messages = ["message1", "message2", "message3"]

        for message in previous_messages:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "message": message}
            )

    async def chat_message(self, event):
        message = event["message"]
        # send message to websocket
        await self.send(text_data=json.dumps({"message": message}))
