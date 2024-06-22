from django.shortcuts import render, redirect
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse

from .forms import *
from .models import Pdf, Tag



@login_required
def pdf_overview(request):
    return render(request, 'overview.html', {'profile': request.user.profile})


@login_required
# def view_pdf_view(request, pdf_uuid):
def view_pdf_view(request):
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


@login_required
def delete_pdf_view(request, pdf_id):
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)
        pdf.delete()
    except:
        pass
    
    return redirect('pdf_overview')


@login_required
def download_pdf_view(request, pdf_id):
    user_profile = request.user.profile
    pdf = user_profile.pdf_set.get(id=pdf_id)
    file_name = pdf.name.replace(' ', '_').lower()
    response = FileResponse(open(pdf.file.path, "rb"), as_attachment=True, filename=file_name)

    return response
