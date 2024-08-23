from django.contrib import admin
from .models import WritingRule

@admin.register(WritingRule)
class WritingRuleAdmin(admin.ModelAdmin):
    list_display = ('lead_writer', 'rule_text', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('rule_text', 'lead_writer__username')
    ordering = ('-created_at',)
    readonly_fields = ('lead_writer', 'created_at', 'updated_at')
    