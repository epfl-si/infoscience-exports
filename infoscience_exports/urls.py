from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from django_tequila.urls import urlpatterns as django_tequila_urlpatterns

app_patterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('exports.urls')),

    url(r'^logged-out/$', TemplateView.as_view(template_name='log_out.html')),
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

if settings.DEBUG:
    import debug_toolbar

    if settings.SITE_PATH and settings.SITE_PATH.strip('/'):
        urlpatterns = [
            url(r'^%s/__debug__/' % settings.SITE_PATH.strip('/'), include(debug_toolbar.urls)),
        ] + urlpatterns
    else:
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
