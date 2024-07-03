from django.urls import path
from users.views import profile_delete, profile_emailchange, profile_settings_view

urlpatterns = [
    path('settings', profile_settings_view, name="profile-settings"),
    path('emailchange', profile_emailchange, name="profile-emailchange"),
    path('delete', profile_delete, name="profile-delete"),
]
