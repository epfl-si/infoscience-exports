from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin
from django.conf import settings
from django.contrib.auth.forms import UsernameField
from django_tequila.admin import TequilaAdminSite
from django.utils.translation import gettext_lazy as _

from log_utils import LoggedModelAdminMixin
from .models import Export, User


admin.autodiscover()
admin.site.site_url = settings.SITE_PATH
admin.site.site_header = "Infoscience-Exporter Admin"
admin.site.site_title = "Publication lists exporter"
admin.site.__class__ = TequilaAdminSite


class UserChangeForm(forms.ModelForm):
    # remove the mandatory password
    password1 = forms.HiddenInput()

    class Meta:
        model = User
        fields = '__all__'
        field_classes = {'username': UsernameField}


class UserCreationForm(forms.ModelForm):
    # remove the mandatory password
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = ''
        # user.set_unusable_password()
        if commit:
            user.save()
        return user


class EPFLUserModelAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    add_form_template = 'admin/add_user_form.html'
    list_display = ('username', 'email', 'last_login', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('EPFL info'), {'fields': ('sciper', 'where', 'units', 'group', 'classe', 'statut')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # remove password from form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email'),
        }),
    )


class ExportLoggedModelAdmin(LoggedModelAdminMixin, ModelAdmin):
    list_display = ('name', 'user', 'get_absolute_url', 'updated_at')
    list_filter = ('updated_at', )


admin.site.register(Export, ExportLoggedModelAdmin)
admin.site.register(User, EPFLUserModelAdmin)
