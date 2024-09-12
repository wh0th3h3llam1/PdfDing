from admin.views import AdjustAdminRights, DeleteProfile, Overview
from django.urls import path

urlpatterns = [
    path('', Overview.as_view(), name='admin_overview'),
    path('<int:page>/', Overview.as_view(), name='admin_overview_page'),
    path('rights/<identifier>', AdjustAdminRights.as_view(), name='admin_adjust_rights'),
    path('delete/<identifier>', DeleteProfile.as_view(), name='admin_delete_profile'),
]
