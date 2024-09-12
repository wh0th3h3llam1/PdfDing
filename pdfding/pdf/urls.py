import pdf.views.pdf_views as pdf_views
import pdf.views.share_views as share_views
from django.urls import path

urlpatterns = [
    path('', pdf_views.Overview.as_view(), name='pdf_overview'),
    path('<int:page>/', pdf_views.Overview.as_view(), name='pdf_overview_page'),
    path('add', pdf_views.Add.as_view(), name='add_pdf'),
    path('current_page/<identifier>', pdf_views.CurrentPage.as_view(), name='current_page'),
    path('delete/<identifier>', pdf_views.Delete.as_view(), name='delete_pdf'),
    path('details/<identifier>', pdf_views.Details.as_view(), name='pdf_details'),
    path('download/<identifier>', pdf_views.Download.as_view(), name='download_pdf'),
    path('edit/<identifier>/<field_name>', pdf_views.Edit.as_view(), name='edit_pdf'),
    path('get/<identifier>', pdf_views.Serve.as_view(), name='serve_pdf'),
    path('update_page', pdf_views.UpdatePage.as_view(), name='update_page'),
    path('view/<identifier>', pdf_views.View.as_view(), name='view_pdf'),
    path('share/<identifier>', share_views.Share.as_view(), name='share_pdf'),
    path('shared/overview/', share_views.Overview.as_view(), name='shared_pdf_overview'),
    path('shared/overview/<int:page>/', share_views.Overview.as_view(), name='shared_pdf_overview_page'),
    path('shared/delete/<identifier>', share_views.Delete.as_view(), name='delete_shared_pdf'),
    path('shared/details/<identifier>', share_views.Details.as_view(), name='shared_pdf_details'),
    path('shared/download/<identifier>', share_views.Download.as_view(), name='download_shared_pdf'),
    path('shared/edit/<identifier>/<field_name>', share_views.Edit.as_view(), name='edit_shared_pdf'),
    path('shared/get/<identifier>', share_views.Serve.as_view(), name='serve_shared_pdf'),
    path('shared/<identifier>', share_views.ViewShared.as_view(), name='view_shared_pdf'),
]
