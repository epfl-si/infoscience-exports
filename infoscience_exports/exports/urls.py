from django.conf.urls import url, include
from exports import views

export_patterns = ([
    url(r'^$', views.ExportList.as_view(), name='export-list'),

    url(r'^(?P<pk>\d+)/$',
        views.ExportView.as_view(template_name="exports/export.html"),
        name='export-view'),

    url(r'^new/$', views.ExportCreate.as_view(), name='export-create'),
    url(r'^(?P<pk>\d+)/update/$', views.ExportUpdate.as_view(), name='export-update'),
    url(r'^(?P<pk>\d+)/update/to-dynamic-list/$', views.ExportUpgrade.as_view(), name='export-update-to-dynamic-list'),
    url(r'^(?P<pk>\d+)/delete/$', views.ExportDelete.as_view(), name='export-delete'),
    url(r'^preview/$', views.preview, name='export-preview'),
    # this one is used to show a full export saved in db aside the preview
    url(r'^(?P<pk>\d+)/compare/$', views.compare_with_preview, name='export-compare'),
    url(r'^version/$', views.version),
    url(r'^version/(?P<label>\w+)/$', views.version, name='export-version'),
    ], 'exports')

urlpatterns = [
    url(r'^', include(export_patterns, namespace='crud')),
]
