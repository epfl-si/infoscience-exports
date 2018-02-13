from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^', include('exports.urls')),

    url(r'^api/v1/', include(router.urls)),

    url(r'^api/v1/', include('exports.api')),
    url(r'^mock/v1/', include('exports.mock')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
