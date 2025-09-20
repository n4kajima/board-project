# core/templatetags/core_extras.py
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from urllib.parse import urlencode
import re
from pathlib import Path

register = template.Library()


@register.simple_tag(takes_context=True)
def qreplace(context, **kwargs):
    """
    現在のクエリストリングを保ったまま、指定キーだけ置き換えたURLパラメータを返す。
    例）<a href="?{% qreplace status='open' %}">
    """
    request = context.get("request")
    query = request.GET.copy() if request and hasattr(request, "GET") else {}
    for k, v in kwargs.items():
        if v is None or v == "":
            query.pop(k, None)
        else:
            query[k] = v
    return urlencode(query, doseq=True)


@register.filter
def highlight(text, term):
    """
    検索語を <mark> で強調（大文字小文字を無視）。XSS対策のためエスケープしてから置換。
    例）{{ q.title|highlight:request.GET.q }}
    """
    if not text or not term:
        return escape(text or "")
    try:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        def repl(m):
            return f"<mark>{escape(m.group(0))}</mark>"
        escaped = escape(str(text))
        result = pattern.sub(repl, escaped)
        return mark_safe(result)
    except re.error:
        return escape(text)


@register.filter
def is_owner(obj, user):
    """
    オブジェクト（Question/Answerなど）のauthorが自分か判定。
    例）{% if q|is_owner:user %} ... {% endif %}
    """
    if not hasattr(obj, "author"):
        return False
    return bool(user and obj.author_id == getattr(user, "id", None))


@register.filter
def basename(path_or_url: str):
    """
    パス/URLからファイル名だけ取得。
    例）{{ att.image.url|basename }}
    """
    if not path_or_url:
        return ""
    # URLでもPathでもだいたいOK
    try:
        return Path(str(path_or_url)).name
    except Exception:
        return str(path_or_url).split("/")[-1]


@register.simple_tag
def badge_for_status(status):
    """
    質問ステータスに応じたBootstrapバッジのclass名を返す。
    例）<span class="badge {{ badge_for_status(q.status) }}">...</span>
    """
    mapping = {
        "open": "bg-primary",
        "answered": "bg-success",
        "canceled": "bg-secondary",
    }
    return mapping.get(status, "bg-light text-dark")
