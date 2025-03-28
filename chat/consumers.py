import json
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Group, Message


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f"chat_{self.group_id}"
        self.user = self.scope['user']

        if await self.is_member():
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()
    

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        content = data['content']
        file_url = data['file_url']

        message = await self.save_message(content, file_url) 

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {
                    'sender': self.user.username,
                    'content': content,
                    'file_url': file_url,
                    'timestamp': message.timestamp.isoformat()
                }
            }
        )

    
    async def chat_message(self, event):
        await self.send(json.dumps(event['message']))


    @database_sync_to_async
    def is_member(self):
        return Group.objects.filter(id=self.group_id, members=self.user).exists()


    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        await self.send(text_data=json.dumps({'message': message, 'user': user}))


    @database_sync_to_async
    def save_message(self, content, file_url):
        return Message.objects.create(
            sender = self.user,
            group_id=self.group_id,
            content=content,
            file=file_url if file_url else None
        )    



class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.recipient_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = self.get_room_name(self.user.id, int(self.recipient_id))

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content')
        file_url = data.get('file_url')

        # Save message to database
        message = await self.save_message(content, file_url)

        # Send message to both users
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': {
                    'sender': self.user.username,
                    'content': content,
                    'file_url': file_url,
                    'timestamp': message.timestamp.isoformat()
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    def get_room_name(self, user1_id, user2_id):
        # Unique room name for chat between two users
        return f'private_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}'

    @database_sync_to_async
    def save_message(self, content, file_url):
        recipient = User.objects.get(id=self.recipient_id)
        return Message.objects.create(
            sender=self.user,
            recipient=recipient,
            content=content,
            file=file_url if file_url else None
        )

    