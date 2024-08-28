from django.urls import path
from pdf.views.pdf_views import Add, CurrentPage, Delete, Details, Download, Edit, Overview, Serve, UpdatePage, View

urlpatterns = [
    path('', Overview.as_view(), name='pdf_overview'),
    path('<int:page>/', Overview.as_view(), name='pdf_overview_page'),
    path('add', Add.as_view(), name='add_pdf'),
    path('current_page/<pdf_id>', CurrentPage.as_view(), name='current_page'),
    path('delete/<pdf_id>', Delete.as_view(), name='delete_pdf'),
    path('details/<pdf_id>', Details.as_view(), name='pdf_details'),
    path('download/<pdf_id>', Download.as_view(), name='download_pdf'),
    path('edit/<pdf_id>/<field_name>', Edit.as_view(), name='edit_pdf'),
    path('get/<pdf_id>', Serve.as_view(), name='serve_pdf'),
    path('update_page', UpdatePage.as_view(), name='update_page'),
    path('view/<pdf_id>', View.as_view(), name='view_pdf'),
]
