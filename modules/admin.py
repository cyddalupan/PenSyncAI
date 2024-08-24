from django.contrib import admin

from rules.models import WritingRule
from .models import Module, Article
from ckeditor.widgets import CKEditorWidget
from django.db import models
from django.utils.html import format_html
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI()

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
        score, suggestion = ai_check_write(obj.content)
        obj.score = score
        obj.feedback = suggestion
        if not change or not obj.writer_id:
            obj.writer = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Only allow the writer or a superuser to edit the article
        if obj and not request.user.is_superuser and obj.writer != request.user:
            return False
        return super().has_change_permission(request, obj)

def ai_check_write(article):
    active_rules = WritingRule.objects.filter(is_active=True).order_by('created_at')
    rules_text = " ".join([rule.rule_text for rule in active_rules])
    system_message = f"Trigger the score_article function no need for reply. You rate the user article based on these rules: {rules_text}"
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": article},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "score_article",
                        "description": "this function always triggers. this gives the article score and suggestion on how to improve the score",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "score": {
                                    "type": "integer",
                                    "description": "Score of the writter on how good it follows the rules from 1 to 100. 100 is perfect.",
                                },
                                "suggestion": {
                                    "type": "string",
                                    "description": "Suggestion for the writter on how to get a higher score. just congratulate if the score is perfect",
                                },
                            },
                            "required": ["score"],
                        },
                    },
                },
            ],
        )
        tool_calls = completion.choices[0].message.tool_calls
        
        if tool_calls:
            function_name = tool_calls[0].function.name 
            arguments = tool_calls[0].function.arguments 
            arguments_dict = json.loads(arguments)
            
            if function_name == "score_article":
                score = arguments_dict['score']
                suggestion = arguments_dict['suggestion']
                return score, suggestion
            else:
                return None, None
    except Exception as e:
        return None, None