from django.urls import path
from users.views import Delete, ChangeEmail, settings

urlpatterns = [
    path('settings', settings, name="profile-settings"),
    path('change_email', ChangeEmail.as_view(), name="profile-emailchange"),
    path('delete', Delete.as_view(), name="profile-delete"),
]
