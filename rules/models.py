from django.db import models
from django.contrib.auth.models import User

class WritingRule(models.Model):
    lead_writer = models.ForeignKey(User, on_delete=models.CASCADE)
    # Assuming User is your Lead Writer model, if not, replace with appropriate model
    
    rule_text = models.TextField()
    # The actual rule content that will be used for comparison
    
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp for when the rule was created
    
    updated_at = models.DateTimeField(auto_now=True)
    # Timestamp for when the rule was last updated
    
    is_active = models.BooleanField(default=True)
    # Allows the Lead Writer to activate/deactivate rules without deleting them

    def __str__(self):
        return f"Rule by {self.lead_writer.username} (Created: {self.created_at})"
