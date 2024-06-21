from django.shortcuts import render, redirect
from django.forms import ValidationError
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pdf, Tag
from uuid import uuid4
from core.settings import MEDIA_ROOT


@login_required
def pdf_overview(request):
    return render(request, 'overview.html', {'profile': request.user.profile})


@login_required
def add_pdf_view(request):
    form = AddForm()  

    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES, owner=request.user.profile)

        context = {}
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.owner = request.user.profile
            pdf.filename = f'{uuid4()}.pdf'
            handle_uploaded_file(request.FILES["file"], request.user.id, pdf.filename)  
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


def handle_uploaded_file(file, user_id, file_name):
    file_path = MEDIA_ROOT / str(user_id) / file_name

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)

    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)