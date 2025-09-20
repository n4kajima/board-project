

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Question(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "質問中"
        ANSWERED = "answered", "回答済み"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    canceled = models.BooleanField(default=False)

    def __str__(self): return f"{self.title}"

class Attachment(models.Model):
    image = models.ImageField(upload_to="attachments/", null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AnswerReply(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
