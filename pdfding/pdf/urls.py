import pdf.views.pdf_views as pdf_views
import pdf.views.share_views as share_views
from django.urls import path

urlpatterns = [
    path('', pdf_views.Overview.as_view(), name='pdf_overview'),
    path('<int:page>/', pdf_views.Overview.as_view(), name='pdf_overview_page'),
    path('add', pdf_views.Add.as_view(), name='add_pdf'),
    path('current_page/<pdf_id>', pdf_views.CurrentPage.as_view(), name='current_page'),
    path('delete/<pdf_id>', pdf_views.Delete.as_view(), name='delete_pdf'),
    path('details/<pdf_id>', pdf_views.Details.as_view(), name='pdf_details'),
    path('download/<pdf_id>', pdf_views.Download.as_view(), name='download_pdf'),
    path('edit/<pdf_id>/<field_name>', pdf_views.Edit.as_view(), name='edit_pdf'),
    path('get/<pdf_id>', pdf_views.Serve.as_view(), name='serve_pdf'),
    path('update_page', pdf_views.UpdatePage.as_view(), name='update_page'),
    path('view/<pdf_id>', pdf_views.View.as_view(), name='view_pdf'),
    path('shared', share_views.Overview.as_view(), name='shared_overview'),
    path('shared/<int:page>/', share_views.Overview.as_view(), name='shared_overview_page'),
    path('share/<pdf_id>', share_views.Share.as_view(), name='share_pdf'),
    path('share/delete/<shared_id>', share_views.Delete.as_view(), name='delete_share'),
    # path('share/details/<shared_id>', share_views.Details.as_view(), name='share_details'),
]
