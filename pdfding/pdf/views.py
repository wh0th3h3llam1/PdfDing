from django.shortcuts import render, redirect
from django.forms import ValidationError
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pdf, Tag
from uuid import uuid4


@login_required
def pdf_overview(request):
    return render(request, 'overview.html', {'profile': request.user.profile})


@login_required
def view_pdf_view(request, pdf_uuid):
    return render(request, 'view_pdf.html')



@login_required
def add_pdf_view(request):
    form = AddForm()  

    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES, owner=request.user.profile)

        context = {}
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.owner = request.user.profile
            pdf.save()

            tag_string = form.data["tag_string"]
            # get unique tag names
            tag_names = Tag.parse_tag_string(tag_string)
            tags = []
            for tag_name in tag_names:
                try:
                    tag = Tag.objects.get(owner=request.user.profile, name=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag(name=tag_name, owner=request.user.profile)
                    tag.save()
                
                tags.append(tag)

            pdf.tags.set(tags)

            return redirect('pdf_overview')

    return render(request, 'add_pdf.html', {'form': form})
