from django.conf.urls import url, include
from exports import views


export_patterns = [
    url(r'^$', views.ExportList.as_view(), name='export-list', ),
    url(r'^new/$', views.ExportCreate.as_view(), name='export-create'),
    url(r'^(?P<pk>\d+)/$', views.ExportDetail.as_view(), name='export-detail'),
    url(r'^(?P<pk>\d+)/update/$', views.ExportUpdate.as_view(),
        name='export-update'),
    url(r'^(?P<pk>\d+)/delete/$', views.ExportDelete.as_view(),
        name='export-delete'),
]

crud_patterns = [
    url(r'^exports/', include(export_patterns)),
]

urlpatterns = [
    url(r'^', include(crud_patterns, namespace='crud')),
]
