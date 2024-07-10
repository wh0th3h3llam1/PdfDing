from django.forms import ModelForm
from django import forms
from django.http.request import QueryDict
from .models import Pdf


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
        self.owner = kwargs.pop('owner', None)

        super(AddForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data

        if not self.owner:
            raise forms.ValidationError('Owner is missing!')

        return cleaned_data

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

        return file


def get_detail_form_class(field_name: str, instance: Pdf, data: QueryDict = None) -> forms.ModelForm:
    """
    When editing a PDFs attributes in the details page a user can change the name, tags and description. Depending
    on the which attribute will be changed the corresponding form will be returned. The returned form will be displayed
    inline.
    """

    class DetailForm(forms.ModelForm):
        """
        The form for changing an attribute of a pdf file. Depending on the context it will be used for editing the name,
        description or tags of a PDF file.
        """

        if field_name == 'tags':
            tag_string = forms.CharField(
                widget=forms.TextInput(attrs={'rows': 3, 'class': 'form-control'}),
            )

        class Meta:
            model = Pdf
            if field_name != 'tags':
                fields = [field_name]
            else:
                fields = []

        def clean_name(self) -> str:  # pragma: no cover
            """Clean the submitted pdf name. Removes trailing and multiple whitespaces."""
            pdf_name = clean_name(self.cleaned_data['name'])

            return pdf_name

    # use the data coming from the post request
    if data:
        form = DetailForm(instance=instance, data=data)
    # get request won't use data
    else:
        if field_name == 'tags':
            # fill the text input field with the current tags
            tags = [tag.name for tag in instance.tags.all()]
            form = DetailForm(instance=instance, initial={'tag_string': ' '.join(sorted(tags))})
        else:
            form = DetailForm(instance=instance)

    return form


def clean_name(pdf_name: str) -> str:
    """Clean the submitted pdf name. Removes trailing and multiple whitespaces."""

    pdf_name.strip()
    pdf_name = ' '.join(pdf_name.split())

    return pdf_name
