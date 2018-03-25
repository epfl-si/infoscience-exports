from django.urls import reverse
from django.db import models
from django.conf import settings

from auditlog.registry import auditlog
from dirtyfields import DirtyFieldsMixin

from .settings import BulletsSettings, ThumbnailSettings, LinksSettings, \
    GroupBySettings, PendingPublicationsSettings, FormatsSettings, \
    AdvancedOptionsSettings, SummarySettings


class Export(BulletsSettings,
             ThumbnailSettings,
             SummarySettings,
             LinksSettings,
             GroupBySettings,
             PendingPublicationsSettings,
             FormatsSettings,
             AdvancedOptionsSettings,
             models.Model,
             DirtyFieldsMixin,
             ):
    """
    This should be the only no abstract model, reuniting all the settings
    trough inheritance of abstracts models
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.TextField()

    def __str__(self):
        return "Export {} {}".format(self.id, self.name)

    def get_absolute_url(self):
        return reverse('crud:export-view', args=[str(self.id)])

    def get_cache_key(self):
        """ build an uniq key per object"""
        return "export_{}".format(self.id)

    class Meta:
        ordering = ['-id']


auditlog.register(Export)
