from django.urls import reverse_lazy as django_reverse_lazy
from django.db import transaction
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _

from rest_framework import viewsets, permissions, mixins
from rest_framework.request import Request

from exports import format_version
from log_utils import LogMixin
from .models import Export
from .serializers import ExportSerializer
from .forms import ExportForm
from .options_notices import get_notices


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


class ExportViewSet(
        UserPassesTestMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    queryset = Export.objects.all()
    serializer_class = ExportSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LoggedExportViewSet(LogMixin, ExportViewSet):
    # log any creation
    def perform_create(self, serializer):
        super(LoggedExportViewSet, self).perform_create(serializer)
        self.logger.info("A new export as been created")


class MockExportViewSet(ExportViewSet):
    queryset = Export.mock_objects.all()

    def dispatch(self, request, *args, **kwargs):
        """
        Don't dispatch the call if the url has the "fake" arg
        """
        query_string = Request(request).query_params
        fake_code = query_string.get('fake')

        if fake_code:
            fake_code = int(fake_code)
            return HttpResponse(status=fake_code)
        else:
            # NB: the 'mock' db is configured with ATOMIC_REQUESTS = True
            sid = transaction.savepoint(using='mock')
            response = super(MockExportViewSet, self).dispatch(request, *args, **kwargs)
            transaction.savepoint_rollback(sid, using='mock')
            return response


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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        options = {}
        options['is_extern'] = True
        options['url'] = self.object.url
        options['format'] = 'SHORT'  # self.object.formats_type
        options['bullet'] = self.object.bullets_type
        options['thumb'] = self.object.show_thumbnail
        options['link_title'] = self.object.show_linkable_titles
        options['link_authors'] = self.object.show_linkable_authors
        options['link_print'] = self.object.show_links_for_printing
        options['link_detailed'] = self.object.show_detailed
        options['link_fulltext'] = self.object.show_fulltext
        options['link_publisher'] = self.object.show_viewpublisher
        options['groupsby_all'] = self.object.groupsby_type
        options['groupsby_year'] = self.object.groupsby_year
        options['groupsby_doc'] = self.object.groupsby_doc
        options['pending_publications'] = self.object.show_pending_publications

        options = get_notices(options)
        context['options'] = options
        return context


def preview(request):
    params = request.GET.dict()

    options = {}
    options['is_extern'] = False
    options['url'] = params['params[url]']
    options['format'] = 'SHORT'  # params['params[format]']
    options['bullet'] = params['params[bullet]']
    options['thumb'] = params['params[thumb]'] == 'true'
    options['link_title'] = params['params[link_title]'] == 'true'
    options['link_authors'] = params['params[link_authors]'] == 'true'
    options['link_print'] = params['params[link_print]'] == 'true'
    options['link_detailed'] = params['params[link_detailed]'] == 'true'
    options['link_fulltext'] = params['params[link_fulltext]'] == 'true'
    options['link_publisher'] = params['params[link_publisher]'] == 'true'
    options['groupsby_all'] = params['params[groupsby_all]']
    options['groupsby_year'] = params['params[groupsby_year]']
    options['groupsby_doc'] = params['params[groupsby_doc]']
    options['pending_publications'] = params['params[pending_publications]'] == 'true'

    options = get_notices(options)
    c = {'options': options}

    t = loader.get_template('exports/export.html')
    return HttpResponse(t.render(c))


def version(request, label='version'):
    return HttpResponse(format_version(label))
