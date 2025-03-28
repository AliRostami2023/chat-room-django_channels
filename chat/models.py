from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=255)  
    members = models.ManyToManyField(User, related_name='chat_groups')  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True) 
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField(blank=True) 
    file = models.FileField(upload_to='chat_files/', null=True, blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
        return f"{self.sender}, {self.recipient}"
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
