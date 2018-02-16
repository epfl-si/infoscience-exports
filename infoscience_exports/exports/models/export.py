from django.urls import reverse
from django.db import models

from dirtyfields import DirtyFieldsMixin

from .settings import BulletsSettings


class Export(BulletsSettings,
             models.Model,
             DirtyFieldsMixin,
             ):
    """
    This should be the only no abstract model, reuniting all the settings
    trough inheritance of abstracts models
    """
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.TextField()

    def __str__(self):
        return "Export {} {}".format(self.id,
                                     self.name)

    def get_absolute_url(self):
        return reverse('crud:export-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-id']


Export.mock_objects = Export.objects.db_manager('mock')
