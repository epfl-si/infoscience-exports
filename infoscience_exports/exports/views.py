from django.urls import reverse_lazy as django_reverse_lazy
from django.db import transaction
from django.http import HttpResponse
from django.template import Context, loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets, permissions, mixins
from rest_framework.request import Request

from log_utils import LogMixin
from .models import Export
from .serializers import ExportSerializer
from .forms import ExportForm
from .marc21xml import import_marc21xml


class ExportViewSet(mixins.ListModelMixin,
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


class ExportCreate(LoginRequiredMixin, CreateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExportCreate, self).form_valid(form)


class ExportUpdate(LoginRequiredMixin, UpdateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')


class ExportDelete(LoginRequiredMixin, DeleteView):
    model = Export
    success_url = django_reverse_lazy('crud:export-list')


class ExportView(DetailView):
    model = Export
    template_name_suffix = ''

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        options = {}
        options['object'] = self.object
        options['is_extern'] = True
        options['marc21xml'] = import_marc21xml(self.object.url)
        options['bullet'] = self.object.bullets_type
        options['thumb'] = self.object.show_thumbnail
        context['options'] = options
        return context


def preview(request):
    params = request.GET.dict()
    url = params['params[url]']
    bullet = params['params[bullet]']
    thumb = params['params[thumb]']
    
    options = {}
    options['is_extern'] = False
    options['marc21xml'] = import_marc21xml(url) if url else ''
    options['bullet'] = bullet
    options['thumb'] = thumb == 'true'
    c = { 'options': options }

    t = loader.get_template('exports/export.html')
    return HttpResponse(t.render(c))
