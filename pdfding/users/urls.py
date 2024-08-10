from django.urls import path
from users.views import ChangeSetting, Delete, settings

urlpatterns = [
    path('settings', settings, name="profile-settings"),
    path('delete', Delete.as_view(), name="profile-delete"),
    path('change_setting/<field_name>', ChangeSetting.as_view(), name="profile-setting-change"),
]
