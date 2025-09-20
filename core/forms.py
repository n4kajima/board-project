# core/forms.py
from django import forms
from .models import Question, Answer, AnswerReply, Subject

# --- ここから追加：複数ファイル対応 ---
class MultiFileInput(forms.ClearableFileInput):
    # これがないと multiple を付けられず、ValueError になります
    allow_multiple_selected = True

class MultiFileField(forms.FileField):
    """
    複数ファイルを受け取れる FileField。
    clean() は [UploadedFile, ...] のリストを返す。
    """
    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super().clean(d, initial) for d in data]
# --- 追加ここまで ---

class QuestionForm(forms.ModelForm):
    images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),  # ← インスタンスで渡す（() が必要）
        help_text="画像を複数アップ可能",
    )
    class Meta:
        model = Question
        fields = ["subject", "title", "body"]

class AnswerForm(forms.ModelForm):
    images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),  # ← 同上
    )
    class Meta:
        model = Answer
        fields = ["body"]

class ReplyForm(forms.ModelForm):
    class Meta:
        model = AnswerReply
        fields = ["body"]

class SearchForm(forms.Form):
    q = forms.CharField(label="検索", required=False)
    status = forms.ChoiceField(
        choices=[("", "両方"), ("open", "質問中"), ("answered", "回答済み")],
        required=False
    )
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False, empty_label="全科目")
