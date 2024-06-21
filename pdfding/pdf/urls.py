from django.urls import path
from pdf.views import *

urlpatterns = [
    path('', pdf_overview, name="pdf_overview"),
    path('add', add_pdf_view, name="add_pdf"),
]
