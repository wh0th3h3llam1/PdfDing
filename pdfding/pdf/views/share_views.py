from django.http import HttpRequest
from django.shortcuts import render
from django.views import View


class Share(View):
    """View for  new PDF files."""

    def get(self, request: HttpRequest, pdf_id: str):
        """Display the form for adding a PDF file."""

        # form = AddForm()

        # return render(request, 'add_pdf.html', {'form': form})
        return render(request, 'share_pdf.html')


class Overview(View):
    def get(self, request: HttpRequest, page: int = 1):
        return render(request, 'share_overview.html')


class Present(View):
    def get(self, request: HttpRequest, share_id: str):
        pass


class View(View):
    pass
