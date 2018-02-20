from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from django_tequila.urls import urlpatterns as django_tequila_urlpatterns

router = DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('exports.urls')),

    url(r'^logged-out/$', TemplateView.as_view(template_name='log_out.html')),

    url(r'^api/v1/', include(router.urls)),

    url(r'^api/v1/', include('exports.api')),
    url(r'^mock/v1/', include('exports.mock')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += django_tequila_urlpatterns
