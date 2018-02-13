from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from exports.views import MockExportViewSet

router = DefaultRouter()
router.register(r'exports', MockExportViewSet)

app_name = 'mock'

urlpatterns = [
    url(r'', include(router.urls)),
]
