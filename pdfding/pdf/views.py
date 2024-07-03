from django.shortcuts import render, redirect
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse, JsonResponse
from django_htmx.http import HttpResponseClientRefresh, HttpResponseClientRedirect
from django.views.static import serve
from django.urls import reverse

from .forms import AddForm, get_detail_form_class
from .models import Pdf, Tag
from core.settings import MEDIA_ROOT


def redirect_overview(request):
    """
    Simple view for redirecting to the pdf overview. This is used when the root url is accessed.

    GET: Redirect to the PDF overview page.
    """

    return redirect('pdf_overview')


@login_required
def pdf_overview(request, page: int = 1):
    """
    View for the PDF overview page. This view performs the searching and sorting of the PDFs. It's also responsible for
    paginating the PDFs.

    GET: Display the PDF overview.
    """

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
def serve_pdf(request, pdf_id: str):
    """
    Returns the PDF file specified by the PDF id.

    GET: Return the specified file as a FileResponse.
    """

    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return serve(request, document_root=MEDIA_ROOT, path=pdf.file.name)
    except ValidationError:
        return


@login_required
def view_pdf_view(request, pdf_id: str):
    """
    The view responsible for displaying the PDF file specified by the PDF id in the browser.

    GET: Display the PDF file in the browser.
    """
    try:
        user_profile = request.user.profile
        user_profile.pdf_set.get(id=pdf_id)

        return render(request, 'view_pdf.html', {'pdf_id': pdf_id})
    except ValidationError:
        messages.error(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')


@login_required
def add_pdf_view(request):
    """
    View for adding new PDF files.

    GET: Display the form for adding a PDF file.
    POST: Create the new PDF object.
    """

    form = AddForm()

    if request.method == 'POST':
        form = AddForm(request.POST, request.FILES, owner=request.user.profile)

        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.owner = request.user.profile
            pdf.save()

            tag_string = form.data['tag_string']
            # get unique tag names
            tag_names = Tag.parse_tag_string(tag_string)
            tags = process_tag_names(tag_names, request)

            pdf.tags.set(tags)

            return redirect('pdf_overview')

    return render(request, 'add_pdf.html', {'form': form})


@login_required
def pdf_details_view(request, pdf_id: str):
    """
    View for displaying the details page of a PDF.

    GET: Display the details page.
    """
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)
        sort_query = request.META['HTTP_REFERER'].split('sort=')
        if len(sort_query) == 1:
            sort_query = ''
        else:
            sort_query = sort_query[-1]

        return render(request, 'details.html', {'pdf': pdf, 'sort_query': sort_query})
    except ValidationError:
        messages.error(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')


@login_required()
def pdf_edit_view(request, pdf_id: str, field: str):
    """
    The view for editing a PDF's name, tags and description. The field, that is to be changed, is specified by the
    'field' argument.

    GET: Triggered by htmx. Display an inline form for editing the correct field.
    POST: Change the specified field by submitting the form.
    """

    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)
    except ValidationError:
        messages.error(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')

    if request.htmx:
        form = get_detail_form_class(field, instance=pdf)
        return render(
            request,
            'partials/details_form.html',
            {'form': form, 'pdf_id': pdf_id, 'field': field},
        )

    if request.method == 'POST':
        form = get_detail_form_class(field, instance=pdf, data=request.POST)

        if form.is_valid():
            # if tags are changed the provided tag string needs to processed, the PDF's tags need updating and orphaned
            # tags need to be deleted.
            if field == 'tags':
                tag_names = form.data['tag_string'].split(' ')

                # check if tag needs to be deleted
                for tag in pdf.tags.all():
                    if tag.name not in tag_names and tag.pdf_set.count() == 1:
                        tag.delete()

                tags = process_tag_names(tag_names, request)

                pdf.tags.set(tags)

            # if the name is changed we need to check that it is a unique name not used by another pdf of this user.
            elif field == 'name':
                existing_pdf = Pdf.objects.filter(owner=request.user.profile, name__iexact=form.data['name']).first()

                if existing_pdf and str(existing_pdf.id) != pdf_id:
                    messages.warning(request, 'This name is already used by another PDF!')
                else:
                    form.save()

            # if description is changed save it
            else:
                form.save()

            return redirect('pdf_details', pdf_id=pdf_id)
        return render(request, 'details.html', {'pdf': pdf})


@login_required
def delete_pdf_view(request, pdf_id):
    """
    View for deleting the PDF specified by its ID.

    DELETE: Delete the specified PDF.
    """

    if request.method == 'DELETE' and request.htmx:
        try:
            user_profile = request.user.profile
            pdf = user_profile.pdf_set.get(id=pdf_id)
            pdf.delete()
        except ValidationError:
            pass
        # try to redirect to current page
        if 'details' not in request.META['HTTP_REFERER']:
            return HttpResponseClientRefresh()
        # if deleted from the details page the details page will no longer exist
        else:
            return HttpResponseClientRedirect(reverse('pdf_overview'))

    return redirect('pdf_overview')


@login_required
def download_pdf_view(request, pdf_id):
    """
    View for downloading the PDF specified by the ID.

    GET: Return the specified file as a FileResponse.
    """

    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)
        file_name = pdf.name.replace(' ', '_').lower()
        response = FileResponse(open(pdf.file.path, 'rb'), as_attachment=True, filename=file_name)

        return response
    except ValidationError:
        messages.warning(request, 'You have no access to the requested PDF File!')
        return redirect('pdf_overview')


def update_page_view(request):
    """
    View for updating the current page of the viewed PDF. This is triggered everytime the page the user changes the
    displayed page in the browser.

    POST: Change the current page.
    """

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
    except ValidationError:
        return HttpResponse(status=403)


def current_page_view(request, pdf_id: str):
    """
    View for getting the current page of a PDF.

    GET: Get the current page of the specified PDF.
    """

    if not request.user.is_authenticated:
        return HttpResponse(status=403)
    if request.method != 'GET':
        return HttpResponse(status=405)
    try:
        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return JsonResponse({'current_page': pdf.current_page}, status=200)
    except ValidationError:
        return HttpResponse(status=403)


def process_tag_names(tag_names: list[str], request) -> list[Tag]:
    """
    Process the specified tags. If the tag is existing it will simply be added to the return list. If it does not
    exist it, it will be created and then be added to the return list.
    """

    tags = []
    for tag_name in tag_names:
        try:
            tag = Tag.objects.get(owner=request.user.profile, name=tag_name)
        except Tag.DoesNotExist:
            tag = Tag(name=tag_name, owner=request.user.profile)
            tag.save()

        tags.append(tag)

    return tags


def process_raw_search_query(raw_search_query: str) -> tuple[str, list[str]]:
    """
    Process the raw search query.

    Example input: #tag1 #tag2 searchstring1 searchstring2
    Example output: ('searchstring1 searchstring2', ['tag1', 'tag2'])
    """

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
