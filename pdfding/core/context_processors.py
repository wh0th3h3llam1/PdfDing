from django.conf import settings
from django.http import HttpRequest


def theme_context(request: HttpRequest):  # pragma: no cover
    return {'DEFAULT_THEME': settings.DEFAULT_THEME, 'DEFAULT_THEME_COLOR': settings.DEFAULT_THEME_COLOR}
