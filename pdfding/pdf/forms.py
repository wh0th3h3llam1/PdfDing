import magic
from django import forms
from django.forms import ModelForm

from .models import Pdf, SharedPdf


class AddForm(ModelForm):
    """Class for creating the form for adding PDFs."""

    tag_string = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add Tags'}),
        help_text='Enter any number of tags separated by space and without the hash (#). '
        'If a tag does not exist it will be automatically created.',
    )

    class Meta:
        model = Pdf
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add PDF Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add Description'}),
            'file': forms.ClearableFileInput(),
        }

        fields = ['name', 'description', 'file']

    def __init__(self, *args, **kwargs):
        """
        Adds the owner profile to the form. This is done, so we can check if the owner already has
        a PDF with the provided name in clean_name.
        """

        self.owner = kwargs.pop('owner', None)

        super(AddForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.owner:
            raise forms.ValidationError('Owner is missing!')

        return self.cleaned_data

    def clean_name(self) -> str:
        """
        Clean the submitted pdf name. Removes trailing and multiple whitespaces. Also checks if the user already
        has an uploaded PDF with the same name.
        """

        pdf_name = clean_name(self.cleaned_data['name'])

        existing_pdf = Pdf.objects.filter(owner=self.owner, name=pdf_name).first()

        if existing_pdf:
            raise forms.ValidationError('A PDF with this name already exists!')

        return pdf_name

    def clean_file(self):
        """Clean the submitted pdf file. Checks if the file as a .pdf/.PDF ending"""

        file = self.cleaned_data['file']

        if file.name.lower().split('.')[-1] != 'pdf':
            raise forms.ValidationError('Uploaded file is not a PDF!')

        # recommend using at least the first 2048 bytes, as less can produce incorrect identification
        file_type = magic.from_buffer(self.cleaned_data['file'].read(2048), mime=True)

        if file_type.lower() != 'application/pdf':
            raise forms.ValidationError('Uploaded file is not a PDF!')

        return file


class DescriptionForm(forms.ModelForm):
    """Form for changing the description of a PDF."""

    class Meta:
        model = Pdf
        fields = ['description']


class NameForm(forms.ModelForm):
    """Form for changing the name of a PDF."""

    class Meta:
        model = Pdf
        fields = ['name']

    def clean_name(self) -> str:  # pragma: no cover
        """Clean the submitted pdf name. Removes trailing and multiple whitespaces."""
        pdf_name = clean_name(self.cleaned_data['name'])

        return pdf_name


class TagsForm(forms.ModelForm):
    """Form for changing the tags of a PDF."""

    tag_string = forms.CharField(widget=forms.TextInput(attrs={'rows': 3, 'class': 'form-control'}))

    class Meta:
        model = Pdf
        fields = []


class ShareForm(forms.ModelForm):
    """Class for creating the form for sharing PDFs."""

    class Meta:
        model = SharedPdf
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add Share Name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a private description'}),
        }

        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        """
        Adds the owner profile to the form. This is done, so we can check if the owner already has
        a PDF with the provided name in clean_name.
        """

        self.owner = kwargs.pop('owner', None)

        super(ShareForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.owner:
            raise forms.ValidationError('Owner is missing!')

        return self.cleaned_data

    def clean_name(self) -> str:
        """
        Clean the submitted share name. Removes trailing and multiple whitespaces. Also checks if the user already
        has a share with the same name.
        """

        share_name = clean_name(self.cleaned_data['name'])

        existing_share = SharedPdf.objects.filter(owner=self.owner, name=share_name).first()

        if existing_share:
            raise forms.ValidationError('A Share with this name already exists!')

        return share_name


class SharedDescriptionForm(forms.ModelForm):
    """Form for changing the description of a shared PDF."""

    class Meta:
        model = SharedPdf
        fields = ['description']


class SharedNameForm(forms.ModelForm):
    """Form for changing the name of a shared PDF."""

    class Meta:
        model = SharedPdf
        fields = ['name']

    def clean_name(self) -> str:  # pragma: no cover
        """Clean the submitted pdf name. Removes trailing and multiple whitespaces."""
        pdf_name = clean_name(self.cleaned_data['name'])

        return pdf_name


def clean_name(pdf_name: str) -> str:
    """Clean the submitted pdf name. Removes trailing and multiple whitespaces."""

    pdf_name.strip()
    pdf_name = ' '.join(pdf_name.split())

    return pdf_name
