from __future__ import unicode_literals

from django.conf import settings
from django.urls import include, re_path, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView


app_patterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('exports.urls')),
    re_path(r'^logged-out/$', TemplateView.as_view(template_name='log_out.html')),
    path("", include("django_epfl_entra_id.urls")),
    path("auth/", include("mozilla_django_oidc.urls")),
]

if settings.SITE_PATH:
    urlpatterns = [
        re_path(
            r'^%s/' % settings.SITE_PATH.strip('/'),
            include(app_patterns)
        ),
    ]
else:
    urlpatterns = app_patterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
