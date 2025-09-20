from django.urls import path
from . import views

urlpatterns = [
    path("", views.question_list, name="question_list"),
    path("my/", views.my_questions, name="my_questions"),
    path("q/new/", views.question_create, name="question_create"),
    path("q/<int:pk>/", views.question_detail, name="question_detail"),
    path("q/<int:pk>/cancel/", views.question_cancel, name="question_cancel"),
    path("q/<int:pk>/answer/", views.answer_create, name="answer_create"),
    path("answer/<int:answer_id>/reply/", views.reply_create, name="reply_create"),
]
