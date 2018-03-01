from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin

from django_tequila.admin import TequilaAdminSite

from log_utils import LoggedModelAdminMixin
from .models import Export, User


admin.autodiscover()
admin.site.__class__ = TequilaAdminSite


class ExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    list_display = ('name', 'user', 'get_absolute_url')


admin.site.register(Export, ExportLoggedModelAdmin)
admin.site.register(User, UserAdmin)
