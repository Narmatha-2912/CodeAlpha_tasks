import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Project

class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        allowed = await self.user_can_access(user.pk, self.project_id)
        if not allowed:
            await self.close()
            return
        self.group_name = f"project_{self.project_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @staticmethod
    async def user_can_access(user_id, project_id):
        from channels.db import database_sync_to_async
        @database_sync_to_async
        def check():
            return Project.objects.filter(pk=project_id).filter(
                models_q(user_id)
            ).exists()
        return await check()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def project_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))

def models_q(user_id):
    from django.db.models import Q
    return Q(owner_id=user_id) | Q(members__id=user_id)
