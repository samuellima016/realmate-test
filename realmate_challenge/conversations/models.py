from django.db import models


class Conversation(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Aberta"),
        ("CLOSED", "Fechada"),
    ]

    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversa {self.id} ({self.status})"


class Message(models.Model):
    DIRECTION_CHOICES = [
        ("SENT", "Enviada"),
        ("RECEIVED", "Recebida"),
    ]

    id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Mensagem {self.id} ({self.direction})"


class WebhookLog(models.Model):
    """Modelo para armazenar logs de eventos do webhook."""
    event = models.CharField(max_length=50)
    conversation_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, default="error")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log do Webhook"
        verbose_name_plural = "Logs do Webhook"

    def __str__(self):
        return f"{self.event} - {self.status} - {self.timestamp}"


