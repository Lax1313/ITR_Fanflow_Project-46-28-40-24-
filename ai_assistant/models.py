from django.conf import settings
from django.db import models


class AssistantQuery(models.Model):
    """Logs every question asked to the AI assistant, and the (Django-
    calculated) context it was answered with, for auditability."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    context_used = models.TextField(blank=True)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:60]
