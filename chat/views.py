from rest_framework import viewsets
from .models import Group, Message
from .serializers import ChatGroupSerializer, MessageSerializer


class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = ChatGroupSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
