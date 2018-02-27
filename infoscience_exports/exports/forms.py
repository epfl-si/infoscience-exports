from django import forms

from log_utils import FormLoggingMixin
from .models import Export


class ExportForm(FormLoggingMixin, forms.ModelForm):

    class Meta:
        model = Export
        fields = ['name', 'url', 'groupsby_type', 'groupsby_year', 'groupsby_doc', 'bullets_type', \
                  'show_thumbnail', 'show_linkable_titles', 'show_linkable_authors', 'show_links_for_printing', \
                  'show_detailed', 'show_fulltext', 'show_viewpublisher']
        widgets= {
            'name': forms.TextInput(
                attrs={
                'placeholder': "",
            }),
            'url': forms.TextInput(attrs={
                'placeholder':"https://infoscience.epfl.ch/search?...",
            }),
        }

