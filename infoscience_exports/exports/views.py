from urllib.parse import unquote

from django.conf import settings
from django.urls import reverse_lazy as django_reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _, get_language
from django.core.cache import cache

from exports import format_version
from log_utils import LogMixin
from .models import Export
from .forms import ExportForm
from .options_notices import get_notices
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

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can edit the publication"))
            return super(ExportUpdate, self).form_invalid(form)

        return super(ExportUpdate, self).form_valid(form)


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
        # language dependant cache
        ln = get_language()
        cache_key = self.object.get_cache_key_for_view(ln)

        if cache_key in cache:
            # do we have the result in the cache?
            rendered_response = cache.get(cache_key)
        else:
            context = self.get_context_data(object=self.object)
            rendered_response = self.render_to_response(context).render()

            # save render in two caches, the temp one from Django here
            cache.set(cache_key, rendered_response)

        # the other one into the 'export.last_rendered_page' model, to get it back when things go blackout
        # this field is reserved for invenio exports only, dspace does not need this mechanism
        if self.object.server_engine == 'invenio':
            self.object.last_rendered_page = rendered_response.rendered_content
            self.object.save()
            # TODO: render it back when appropriate (when env.SERVER_ENGINE == 'dspace' maybe) with
            # self.object.last_rendered_page = django.utils.timezone.now()
            # self.object.save()
            # return HttpResponse(self.object.last_rendered_page)

        return rendered_response

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        options = get_options_from_export_attributes(self.object)
        options = get_notices(options)

        context['options'] = options
        return context


def preview(request):
    params = request.GET.dict()

    options = get_options_from_params(params)

    options = get_notices(options)

    c = {'options': options, 'SITE_PATH': settings.SITE_PATH}

    t = loader.get_template('exports/export_complete.html')
    return HttpResponse(t.render(c))


def version(request, label='version'):
    return HttpResponse(format_version(label))
