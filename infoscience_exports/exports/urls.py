from django.conf.urls import url, include
from exports import views

export_patterns = ([
    url(r'^$', views.ExportList.as_view(), name='export-list'),
    url(r'^(?P<pk>\d+)/$', views.ExportView.as_view(), name='export-view'),
    url(r'^new/$', views.ExportCreate.as_view(), name='export-create'),
    url(r'^(?P<pk>\d+)/update/$', views.ExportUpdate.as_view(), name='export-update'),
    url(r'^(?P<pk>\d+)/delete/$', views.ExportDelete.as_view(), name='export-delete'),
    url(r'^preview/$', views.preview, name='export-preview'),
    url(r'^version/$', views.version),
    url(r'^version/(?P<label>\w+)/$', views.version, name='export-version'),
    ], 'exports')

urlpatterns = [
    url(r'^', include(export_patterns, namespace='crud')),
]
