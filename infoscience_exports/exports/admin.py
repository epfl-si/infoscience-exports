from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin
from django.conf import settings
from django_tequila.admin import TequilaAdminSite
from django.utils.translation import gettext_lazy as _

from log_utils import LoggedModelAdminMixin
from .models import Export, User


admin.autodiscover()
admin.site.site_url = settings.SITE_PATH
admin.site.site_header = "Infoscience-Exporter Admin"
admin.site.site_title = "Publication lists exporter"
admin.site.__class__ = TequilaAdminSite


class EPFLUserModelAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('EPFL info'), {'fields': ('sciper', 'where', 'units', 'group', 'classe', 'statut', 'memberof')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class ExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    list_display = ('name', 'user', 'get_absolute_url', 'updated_at')
    list_filter = ('updated_at', )


admin.site.register(Export, ExportLoggedModelAdmin)
admin.site.register(User, EPFLUserModelAdmin)
