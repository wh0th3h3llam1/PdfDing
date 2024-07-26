from django.urls import path
from admin.views import Overview, AdjustAdminRights, DeleteProfile

urlpatterns = [
    path('', Overview.as_view(), name='admin_overview'),
    path('<int:page>/', Overview.as_view(), name='admin_overview_page'),
    path('rights/<user_id>', AdjustAdminRights.as_view(), name='admin_adjust_rights'),
    path('delete/<user_id>', DeleteProfile.as_view(), name='admin_delete_profile'),
]
