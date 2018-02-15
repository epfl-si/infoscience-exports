from django.urls import reverse_lazy as django_reverse_lazy
from django.db import transaction
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, \
    DeleteView

from rest_framework import viewsets, permissions, mixins
from rest_framework.request import Request

from log_utils import LogMixin
from .models import Export
from .serializers import ExportSerializer
from .forms import ExportForm


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
            response = super(MockExportViewSet, self).dispatch(request,
                                                             *args, **kwargs)
            transaction.savepoint_rollback(sid, using='mock')
            return response


class ExportList(LogMixin, ListView):
    model = Export
    paginate_by = 20

    def get(self, *args, **kwargs):
        to_return = super(ExportList, self).get(*args, **kwargs)
        self.logger.info("Get a list of exports")
        return to_return


class ExportCreate(CreateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')


class ExportDetail(DetailView):
    model = Export


class ExportUpdate(UpdateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')


class ExportDelete(DeleteView):
    model = Export
    success_url = django_reverse_lazy('crud:export-list')
