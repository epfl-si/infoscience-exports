from django.urls import re_path, include
from exports import views

export_patterns = ([
    re_path(r'^$', views.ExportList.as_view(), name='export-list'),

    re_path(r'^(?P<pk>\d+)/$',
        views.ExportView.as_view(template_name="exports/export.html"),
        name='export-view'),

    re_path(r'^new/$', views.ExportCreate.as_view(), name='export-create'),
    re_path(r'^(?P<pk>\d+)/update/$', views.ExportUpdate.as_view(), name='export-update'),
    re_path(r'^(?P<pk>\d+)/update/to-dynamic-list/$', views.ExportMigrate.as_view(), name='export-migrate'),
    re_path(r'^(?P<pk>\d+)/delete/$', views.ExportDelete.as_view(), name='export-delete'),
    re_path(r'^preview/$', views.preview, name='export-preview'),
    # this one is used to show a full export saved in db aside the preview
    re_path(r'^(?P<pk>\d+)/compare/$', views.compare_with_preview, name='export-compare'),
    re_path(r'^version/$', views.version),
    re_path(r'^version/(?P<label>\w+)/$', views.version, name='export-version'),
    ], 'exports')

urlpatterns = [
    re_path(r'^', include(export_patterns, namespace='crud')),
]
