from rest_framework import serializers
from .models import Message, Group


class ChatGroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'created_at']

    def get_members(self, obj):
        return [member.username for member in obj.members.all()]


class MessageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    sender = serializers.CharField(source='sender.username', read_only=True)  
    recipient = serializers.CharField(source='recipient.username', read_only=True)
    group = serializers.CharField(source='group.name', read_only=True) 

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'group', 'content', 'file', 'file_url', 'timestamp']

    def get_file_url(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None

