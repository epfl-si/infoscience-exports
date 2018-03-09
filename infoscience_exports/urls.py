from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework.routers import DefaultRouter

from django_tequila.urls import urlpatterns as django_tequila_urlpatterns

router = DefaultRouter()

app_patterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('exports.urls')),

    url(r'^logged-out/$', TemplateView.as_view(template_name='log_out.html')),

    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include('exports.api')),
    url(r'^mock/v1/', include('exports.mock')),
]

app_patterns += django_tequila_urlpatterns

if settings.SITE_PATH:
    urlpatterns = [
        url(
            r'^%s/' % settings.SITE_PATH.strip('/'),
            include(app_patterns)
        ),
    ]
else:
    urlpatterns = app_patterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# FIXME: to remove once nginx is intalled on TIND infrastructure
urlpatterns += staticfiles_urlpatterns()
