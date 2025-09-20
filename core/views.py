
# Create your views here.
# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib import messages
from django.db import transaction

from .models import Question, Answer, AnswerReply, Attachment, Subject
from .forms import QuestionForm, AnswerForm, ReplyForm, SearchForm



def _apply_filters(request, qs):
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")
    subject_id = request.GET.get("subject", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
    if status in ("open", "answered"):
        qs = qs.filter(status=status)
    if subject_id:
        qs = qs.filter(subject_id=subject_id)
    return qs


def question_list(request):
    qs = (
        Question.objects.filter(canceled=False)
        .select_related("subject", "author")
        .annotate(answer_count=Count("answers"))
        .order_by("-created_at")
    )
    qs = _apply_filters(request, qs)
    form = SearchForm(request.GET or None)
    subjects = Subject.objects.all()
    ctx = {"questions": qs, "form": form, "subjects": subjects}
    return render(request, "question_list.html", ctx)


@login_required
def my_questions(request):
    qs = Question.objects.filter(author=request.user).order_by("-created_at")
    qs = _apply_filters(request, qs)
    form = SearchForm(request.GET or None)
    subjects = Subject.objects.all()
    return render(
        request,
        "question_list.html",
        {"questions": qs, "form": form, "subjects": subjects, "mine": True},
    )


@login_required
@transaction.atomic
def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            q = form.save(commit=False)
            q.author = request.user
            q.save()

            # 画像をそのまま添付（OCRは行わない）
            files = form.cleaned_data.get("images") or []
            for f in files:
                Attachment.objects.create(question=q, image=f)

            messages.success(request, "質問を投稿しました。")
            return redirect("question_detail", pk=q.pk)
    else:
        form = QuestionForm()
    return render(request, "question_form.html", {"form": form})


def question_detail(request, pk):
    q = get_object_or_404(Question, pk=pk)
    answer_form = AnswerForm()
    reply_form = ReplyForm()
    return render(
        request,
        "question_detail.html",
        {"q": q, "answer_form": answer_form, "reply_form": reply_form},
    )


@login_required
def question_cancel(request, pk):
    q = get_object_or_404(Question, pk=pk)
    if q.author != request.user:
        messages.error(request, "取消できるのは投稿者のみです。")
        return redirect("question_detail", pk=pk)
    q.canceled = True
    q.save()
    messages.success(request, "質問を取り消しました。")
    return redirect("question_list")


@login_required
@transaction.atomic
def answer_create(request, pk):
    q = get_object_or_404(Question, pk=pk)

    if q.canceled:
        messages.error(request, "取消済みの質問には回答できません。")
        return redirect("question_detail", pk=pk)

    form = AnswerForm(request.POST, request.FILES)
    if not form.is_valid():
        # ここでエラーを question_detail.html に表示できる
        return render(
            request,
            "question_detail.html",
            {"q": q, "answer_form": form, "reply_form": ReplyForm()},
            status=400,
        )

    ans = form.save(commit=False)
    ans.author = request.user
    ans.question = q
    ans.save()

    # 複数画像の添付（OCRなし）
    files = form.cleaned_data.get("images") or []
    for f in files:
        Attachment.objects.create(answer=ans, image=f)

    # 回答が付いたらステータスを回答済みに
    if q.status != Question.Status.ANSWERED:
        q.status = Question.Status.ANSWERED
        q.save(update_fields=["status"])

    messages.success(request, "回答を投稿しました。")
    return redirect("question_detail", pk=pk)


@login_required
def reply_create(request, answer_id):
    ans = get_object_or_404(Answer, pk=answer_id)
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            rep = form.save(commit=False)
            rep.author = request.user
            rep.answer = ans
            rep.save()
            messages.success(request, "返信を投稿しました。")
    return redirect("question_detail", pk=ans.question_id)
