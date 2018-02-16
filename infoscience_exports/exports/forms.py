from django import forms
from django.http import HttpResponseRedirect

from log_utils import FormLoggingMixin
from .models import Export, User


class ExportForm(FormLoggingMixin, forms.ModelForm):
    class Meta:
        model = Export
        exclude = ['user']
        # fields = ['name',
        #           'url',
        #           'bullets_type',
        #           'bullets_type',
        #           ]

