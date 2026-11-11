from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_project(project_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"project_{project_id}",
        {"type": "project.message", "message": message},
    )
