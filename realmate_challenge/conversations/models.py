from django.db import models


class Conversation(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} ({self.status})"


class Message(models.Model):
    DIRECTION_CHOICES = [
        ("SENT", "Sent"),
        ("RECEIVED", "Received"),
    ]

    id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Message {self.id} ({self.direction})"


