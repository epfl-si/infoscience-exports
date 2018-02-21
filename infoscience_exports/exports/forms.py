from django import forms

from log_utils import FormLoggingMixin
from .models import Export


class ExportForm(FormLoggingMixin, forms.ModelForm):
    class Meta:
        model = Export
        fields = ['name', 'url', 'bullets_type', 'show_thumbnail']
