from django.urls import path
from users.views import Delete, ChangeDarkMode, ChangeEmail, settings

urlpatterns = [
    path('settings', settings, name="profile-settings"),
    path('change_email', ChangeEmail.as_view(), name="profile-emailchange"),
    path('change_dark_mode', ChangeDarkMode.as_view(), name="profile-darkmode-change"),
    path('delete', Delete.as_view(), name="profile-delete"),
]
