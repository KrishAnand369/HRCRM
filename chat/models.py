# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    is_private = models.BooleanField(default=False)  # True for private chats, False for group chats

    def __str__(self):
        return self.name if self.name else f"Private Chat ({self.id})"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.room.name}: {self.message[:20]}..."