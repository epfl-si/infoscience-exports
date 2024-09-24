from urllib.parse import unquote

from django.conf import settings
from django.urls import reverse_lazy as django_reverse_lazy, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _, get_language
from django.core.cache import cache

from exports import format_version
from log_utils import LogMixin
from .models import Export
from .forms import ExportForm, ExportMigrateForm
from .options_notices import get_notices
from .url_validator import convert_url_for_dspace
from .options import get_options_from_params, get_options_from_export_attributes


class IsTheUserAccessTest(UserPassesTestMixin):
    # only allow the creator of the object or the staff to access the view
    # trigger the self.get_object()
    raise_exception = True

    def test_func(self):
        # this object's load happens before the view is shown, so we have
        # to cancel other getters
        object = self.get_object()
        return object.user == self.request.user or self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        # overload only to remove self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # overload only to remove self.get_object()
        return super().post(request, *args, **kwargs)


class ExportList(LoginRequiredMixin, LogMixin, ListView):
    model = Export
    paginate_by = 20

    def get(self, *args, **kwargs):
        to_return = super(ExportList, self).get(*args, **kwargs)
        return to_return

    def get_queryset(self):
        return Export.objects.filter(user=self.request.user)


class ExportCreate(LoginRequiredMixin, CreateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')

    def get(self, request, *args, **kwargs):
        # url in parameter is a form initial
        if request.GET.get('url'):
            self.initial.update({
                'url': unquote(request.GET['url']).replace(" ", "+")
            })

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExportCreate, self).form_valid(form)


class ExportUpdate(LoginRequiredMixin, IsTheUserAccessTest, UpdateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')

    def get(self, request, *args, **kwargs):
        export = self.get_object()

        # we don't want anmyore the invenio ones.
        # in case we want to update the data,
        # send the user directly to the upgrade process
        if export.server_engine == 'invenio':
            return HttpResponseRedirect(reverse('crud:export-migrate', args=[export.id]))
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can edit the publication"))
            return super(ExportUpdate, self).form_invalid(form)

        return super(ExportUpdate, self).form_valid(form)


class ExportMigrate(LoginRequiredMixin, IsTheUserAccessTest, UpdateView):
    model = Export
    form_class = ExportMigrateForm
    template_name = 'exports/export_migrate.html'
    success_url = django_reverse_lazy('crud:export-list')

    def get_initial(self):
        initial = super().get_initial()

        initial['url'] = convert_url_for_dspace(self.object.url)
        return initial

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can migrate the publication"))
            return super(ExportMigrate, self).form_invalid(form)

        return super(ExportMigrate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_url'] = self.object.url
        return context

class ExportDelete(IsTheUserAccessTest, LoginRequiredMixin, DeleteView):
    model = Export
    success_url = django_reverse_lazy('crud:export-list')

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can delete the publication"))
            return super(ExportDelete, self).form_invalid(form)

        return super(ExportDelete, self).form_valid(form)


class ExportView(DetailView):
    model = Export
    template_name_suffix = ''

    def get(self, request, *args, **kwargs):
        """ Warning, as we cache the view, don't use any request data"""
        self.object = self.get_object()

        # this field is reserved for invenio exports only, dspace does not need this mechanism
        if self.object.server_engine == 'invenio':
            if self.object.last_rendered_page:
                # this was the long term cache that is not used anymore, set as readonly
                # Now it's time to render what is in the db for invenio
                return HttpResponse(self.object.last_rendered_page)
            else:
                # nothing to return as invenio is no more
                return HttpResponse(status=204)

        # language dependant cache
        ln = get_language()
        cache_key = self.object.get_cache_key_for_view(ln)

        if cache_key in cache:
            # do we have the result in the cache?
            return cache.get(cache_key)
        else:
            # nope, time to render
            context = self.get_context_data(object=self.object)
            rendered_response = self.render_to_response(context).render()

            def has_error_in_options(context):
                return ('options' in context and
                        'error' in context['options'] and
                        context['options']['error'] != '')

            # save render in cache if there is no error
            if not has_error_in_options(context):
                cache.set(cache_key, rendered_response)

            return rendered_response

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        options = get_options_from_export_attributes(self.object)
        options = get_notices(options)

        # knowing from which engine this has been generated on front can be  helpful
        options['server_engine'] = self.object.server_engine

        context['options'] = options
        return context


def preview(request):
    params = request.GET.dict()

    options = get_options_from_params(params)

    options = get_notices(options)

    c = {'options': options, 'SITE_PATH': settings.SITE_PATH}

    t = loader.get_template('exports/export_complete.html')
    return HttpResponse(t.render(c))


def compare_with_preview(request, pk):
    try:
        export = Export.objects.get(id=pk)
    except Export.DoesNotExist:
        raise Http404("Export does not exist")

    c = {'export': export, 'SITE_PATH': settings.SITE_PATH}
    t = loader.get_template('exports/export_compare.html')

    return HttpResponse(t.render(c))


def version(request, label='version'):
    return HttpResponse(format_version(label))
