from django import forms

from log_utils import FormLoggingMixin
from .models import Export


class ExportForm(FormLoggingMixin, forms.ModelForm):

    class Meta:
        model = Export

        exclude = ['user', 'formats_type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ""}),
            'url': forms.TextInput(attrs={'placeholder': "https://infoscience.epfl.ch/search?..."}),
        }
