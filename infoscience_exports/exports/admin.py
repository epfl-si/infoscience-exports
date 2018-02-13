from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from log_utils import LoggedModelAdminMixin
from .models import Export


class ExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    pass

admin.site.register(Export, ExportLoggedModelAdmin)
