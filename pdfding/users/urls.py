from django.urls import path
from users.views import Delete, ChangeTheme, ChangeEmail, settings

urlpatterns = [
    path('settings', settings, name="profile-settings"),
    path('change_email', ChangeEmail.as_view(), name="profile-emailchange"),
    path('change_theme', ChangeTheme.as_view(), name="profile-theme-change"),
    path('delete', Delete.as_view(), name="profile-delete"),
]
