from django.urls import path
from pdf.views import *

urlpatterns = [
    path('', pdf_overview, name='pdf_overview'),
    path('add', add_pdf_view, name='add_pdf'),
    path('delete/<pdf_id>', delete_pdf_view, name='delete_pdf'),
    path('view/<pdf_uuid>', view_pdf_view, name='view_pdf'),
]
