from django.contrib import admin
from .models import Module, Article
from ckeditor.widgets import CKEditorWidget
from django.db import models
from django.utils.html import format_html

class ArticleInline(admin.TabularInline):
    model = Article
    fields = ('title_link', 'writer', 'created_at', 'updated_at', 'score', 'feedback')
    readonly_fields = ('title_link', 'writer', 'created_at', 'updated_at', 'score', 'feedback')
    can_delete = False
    extra = 0

    def title_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.get_admin_url(), obj.title)

    title_link.short_description = 'Title'

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'lead_writer', 'created_at', 'updated_at')
    search_fields = ('title', 'lead_writer__username')
    list_filter = ('created_at', 'lead_writer')
    inlines = [ArticleInline]

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }
    list_display = ('title', 'module', 'writer', 'created_at', 'updated_at', 'score')
    search_fields = ('title', 'writer__username', 'module__title')
    list_filter = ('created_at', 'module', 'writer')
    readonly_fields = ('score', 'feedback', 'writer', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        obj.score = 99
        obj.feedback = "I am Admin"
        if not request.user.is_superuser and not change:
            obj.score = 10
            obj.feedback = "Test"
        if not change or not obj.writer_id:  # If creating a new article
            obj.writer = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Only allow the writer or a superuser to edit the article
        if obj and not request.user.is_superuser and obj.writer != request.user:
            return False
        return super().has_change_permission(request, obj)

