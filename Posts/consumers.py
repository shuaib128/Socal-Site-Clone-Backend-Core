from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .serializers import PostSerializer
from asgiref.sync import sync_to_async
from .models import Post

class PostConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = "post"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def like_post(self, event):
        post_id = event["post_id"]
        Post = await self.get_post(post_id)
        serilizer = await sync_to_async(PostSerializer)(Post)
        
        await self.send_json({
            "post_id": post_id,
            "post": serilizer.data
        })

    @sync_to_async
    def get_post(self, post_id):
        return Post.objects.get(id=post_id)