from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import LoggedExportViewSet

router = DefaultRouter()
router.register(r'exports', LoggedExportViewSet)

urlpatterns = [
    url(r'', include(router.urls, namespace='api')),
]
