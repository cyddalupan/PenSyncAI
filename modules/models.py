from django.urls import reverse
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

class Module(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    lead_writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lead_modules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='articles')
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(null=True, blank=True)  # For storing OpenAI score
    feedback = models.TextField(blank=True, null=True)  # For storing feedback from OpenAI

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.pk])

    def __str__(self):
        return self.title
