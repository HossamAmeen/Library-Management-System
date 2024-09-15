import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['error'] is not None:
            await self.close()
            return
        self.room_group_name = f"user_{self.scope['user_id']}"
        await self.channel_layer.group_add(
                "notifications",
                self.channel_name
        )
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name') and self.room_group_name in \
                self.channel_layer.groups:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def book_available(self, event):
        await self.send(text_data=json.dumps({
            'message': f"The book '{event['title']}' is now available."
        }))
