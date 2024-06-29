from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Pdf


class AddForm(ModelForm):
    tag_string = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add Tags'}),
        help_text='Enter any number of tags separated by space and without the hash (#). If a tag does not exist it will be automatically created.',
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

    def clean_name(self):
        pdf_name = self.cleaned_data["name"]
        # remove trailing whitespaces
        pdf_name.strip()
        # remove multiple whitespaces
        pdf_name = ' '.join(pdf_name.split())

        existing_pdf = Pdf.objects.filter(owner=self.owner, name=pdf_name).first()

        if existing_pdf:
            raise forms.ValidationError("A PDF with this name already exists!")

        return pdf_name

    def clean_file(self):
        file = self.cleaned_data['file']

        if not "pdf" in file.name.lower():
            raise forms.ValidationError("Uploaded file is not a PDF!")

        return file


def get_detail_form_class(field_name, instance, data=None,):
    class DetailForm(forms.ModelForm):
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

    if data:
        form = DetailForm(instance=instance, data=data)
    else:
        if field_name == 'tags':
            tags = [tag.name for tag in instance.tags.all()]
            form = DetailForm(instance=instance, initial={'tag_string': ' '.join(sorted(tags))})
        else:
            form = DetailForm(instance=instance)

    return form


class NameForm(ModelForm):
    # name = forms.CharField(required=True)

    class Meta:
        model = Pdf
        fields = ['name']
