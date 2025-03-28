from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/group/(?P<group_id>\d+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r'ws/private/(?P<user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
]
