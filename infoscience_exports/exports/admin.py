from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin
from django.conf import settings
from django_tequila.admin import TequilaAdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter

from log_utils import LoggedModelAdminMixin
from .models import Export, LegacyExport, User


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


class LegacyExportFilter(SimpleListFilter):
    title = 'exports imported'
    parameter_name = 'Imported'

    def lookups(self, request, model_admin):
        return (('imported','Imported only'),)

    def queryset(self, request, queryset):
        if self.value() == 'imported':
            return queryset.filter(legacyexport__isnull=False)


class LegacyExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    pass


class LegacyExportInline(admin.StackedInline):
    model = LegacyExport
    can_delete = False
    readonly_fields = ('legacy_url',
                       'language',
                       'referenced_url',
                       'origin',
                       'origin_sciper',
                       'raw_csv_entry')


class ExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    list_display = ('name', 'user', 'get_absolute_url', 'updated_at',)
    list_filter = ('updated_at', LegacyExportFilter)
    inlines = [LegacyExportInline]

    def get_formsets_with_inlines(self, request, obj=None):
        """ Only show inline if needed"""
        for inline in self.get_inline_instances(request, obj):
            if obj is not None:
                try:
                    obj.legacyexport
                    yield inline.get_formset(request, obj), inline
                except LegacyExport.DoesNotExist:
                    pass


admin.site.register(Export, ExportLoggedModelAdmin)
admin.site.register(LegacyExport, LegacyExportLoggedModelAdmin)
admin.site.register(User, EPFLUserModelAdmin)
