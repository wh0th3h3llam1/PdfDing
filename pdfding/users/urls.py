from django.urls import path
from users.views import delete, change_email, settings

urlpatterns = [
    path('settings', settings, name="profile-settings"),
    path('change_email', change_email, name="profile-emailchange"),
    path('delete', delete, name="profile-delete"),
]
