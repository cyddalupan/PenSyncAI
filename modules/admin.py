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
    fields = ('title_link', 'writer', 'score', 'sync_level', 'updated_at')
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
    list_display = ('title', 'module', 'writer', 'score', 'sync_level', 'updated_at')
    search_fields = ('title', 'writer__username', 'module__title')
    list_filter = ('created_at', 'module', 'writer')
    readonly_fields = ('score', 'feedback', 'writer', 'sync_level', 'sync_suggestion', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        score, suggestion = ai_check_write(obj.content)
        obj.score = score
        obj.feedback = suggestion

        if not change or not obj.writer_id:
            obj.writer = request.user

        best_article = Article.objects.filter(module=obj.module).order_by('-score').first()

        if best_article and obj.score >= best_article.score:
            obj.sync_level = obj.score
            obj.sync_suggestion = "Great job! The article is well-written and perfectly aligned. No sync needed."
        else:
            sync_level, sync_suggestion = ai_sync_article(best_article.content, obj.content)
            obj.sync_level = sync_level
            obj.sync_suggestion = sync_suggestion


        # Save the object
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
        {"role": "system", "content": "trigger score_article function"},
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
                                    "description": "Score of the writer on how good it follows the rules from 1 to 100. 100 is perfect.",
                                },
                                "suggestion": {
                                    "type": "string",
                                    "description": "Suggestion to the writer on how to get a higher score. use easy to understand words. just congratulate if the score is perfect",
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

def ai_sync_article(best_article, normal_article):
    messages = [
        {"role": "system", "content": "Give me the best_article:"},
        {"role": "user", "content": best_article},
        {"role": "system", "content": "Now Give me the normal article:"},
        {"role": "user", "content": normal_article},
        {"role": "system", "content": "Score how close is the writing style of normal_article to best_article. trigger sync_article function 100 percent of the time"},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "sync_article",
                        "description": "This function triggers 100 percent of the time. Score how close is the writing style of normal_article to best_article and give tips on how to improve the score.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sync_level": {
                                    "type": "integer",
                                    "description": "Score how close is the writing style of normal_article to best_article from 1 to 100. 100 is perfect.",
                                },
                                "sync_suggestion": {
                                    "type": "string",
                                    "description": "Give suggestion to the writer on how to make the writing style of normal_article more close to the style of best_article. dont mention normal_article and best_article. use easy to understand words. just congratulate if the score is perfect",
                                },
                            },
                            "required": ["sync_level"],
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
            
            if function_name == "sync_article":
                sync_level = arguments_dict['sync_level']
                sync_suggestion = arguments_dict['sync_suggestion']
                return sync_level, sync_suggestion
            else:
                return None, None
    except Exception as e:
        return None, None