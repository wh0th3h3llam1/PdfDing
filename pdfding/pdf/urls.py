from django.urls import path
from pdf.views import *

urlpatterns = [
    path('', pdf_overview, name='pdf_overview'),
    path('add', add_pdf_view, name='add_pdf'),
    path('current_page/<pdf_id>', current_page_view, name='current_page'),
    path('delete/<pdf_id>', delete_pdf_view, name='delete_pdf'),
    path('download/<pdf_id>', download_pdf_view, name='download_pdf'),
    path('get/<pdf_id>', serve_pdf, name='serve_pdf'),
    path('update_page', update_page_view, name='update_page'),
    path('view/<pdf_id>', view_pdf_view, name='view_pdf')
]
