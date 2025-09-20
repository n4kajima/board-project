from django.contrib import admin

# Register your models here.
# core/admin.py
from django.contrib import admin
from .models import Subject, Question, Answer, AnswerReply, Attachment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

# 参考：他モデルも見やすく
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "author", "status", "created_at", "canceled")
    list_filter = ("status", "subject", "canceled", "created_at")
    search_fields = ("title", "body", "author__username")
    autocomplete_fields = ("subject", "author")

admin.site.register(Answer)
admin.site.register(AnswerReply)
admin.site.register(Attachment)
