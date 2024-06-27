from django.shortcuts import render, redirect
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.static import serve

from .forms import *
from .models import Tag
from core.settings import MEDIA_ROOT


def redirect_overview(request):
    return redirect('pdf_overview')


@login_required
def pdf_overview(request, page=1):
    sorting_query = request.GET.get('sort', '')
    sorting_dict = {
        '': '-creation_date',
        'newest': '-creation_date',
        'oldest': 'creation_date',
        'title_asc': 'name',
        'title_desc': '-name',
    }

    pdfs = request.user.profile.pdf_set.all().order_by(sorting_dict[sorting_query])

    # filter pdfs
    raw_search_query = request.GET.get('q', '')
    search, tags = process_raw_search_query(raw_search_query)

    for tag in tags:
        pdfs = pdfs.filter(tags__name=tag)

    if search:
        pdfs = pdfs.filter(name__icontains=search)

    paginator = Paginator(pdfs, per_page=15, allow_empty_first_page=True)
    page_object = paginator.get_page(page)

    return render(
        request,
        'overview.html',
        {'page_obj': page_object, 'raw_search_query': raw_search_query, 'sorting_query': sorting_query},
    )


@login_required
def serve_pdf(request, pdf_id):
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return serve(request, document_root=MEDIA_ROOT, path=pdf.file.name)
    except:
        return


@login_required
def view_pdf_view(request, pdf_id):
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return render(request, 'view_pdf.html', {'pdf_id': pdf_id})
    except:
        messages.error(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')


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

            tag_string = form.data['tag_string']
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
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)
        file_name = pdf.name.replace(' ', '_').lower()
        response = FileResponse(open(pdf.file.path, 'rb'), as_attachment=True, filename=file_name)

        return response
    except:
        messages.warning(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')

    return response


def update_page_view(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        user_profile = request.user.profile
        pdf_id = request.POST.get('pdf_id')
        pdf = user_profile.pdf_set.get(id=pdf_id)

        # update current page
        current_page = request.POST.get('current_page')
        pdf.current_page = current_page
        pdf.save()

        return HttpResponse(status=200)
    except:
        return HttpResponse(status=403)


def current_page_view(request, pdf_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    if request.method != 'GET':
        return HttpResponse(status=405)
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return JsonResponse({'current_page': pdf.current_page}, status=200)
    except:
        return HttpResponse(status=403)


def process_raw_search_query(raw_search_query):
    search = []
    tags = []

    if raw_search_query:
        split_query = raw_search_query.split(sep=' ')

        for query in split_query:
            if query.startswith('#'):
                # ignore hashtags only
                if len(query) > 1:
                    tags.append(query[1:])
            elif query:
                search.append(query)

    search = ' '.join(search)

    return search, tags
