from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """Sesión de chat con Google AI"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default='Nueva conversación')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Sesión de Chat'
        verbose_name_plural = 'Sesiones de Chat'

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Mensaje individual en una conversación"""
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('model', 'Modelo IA'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'

    def __str__(self):
        return f"{self.session.id} - {self.role}: {self.content[:50]}"
