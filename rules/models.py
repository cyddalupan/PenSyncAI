from django.db import models
from django.contrib.auth.models import User

class WritingRule(models.Model):
    lead_writer = models.ForeignKey(User, on_delete=models.CASCADE)
    rule_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Rule by {self.lead_writer.username} (Created: {self.created_at})"
