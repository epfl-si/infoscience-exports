from django.core.urlresolvers import reverse
from django.db import models

from dirtyfields import DirtyFieldsMixin


class Export(DirtyFieldsMixin, models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('crud:export-detail', args=[str(self.id)])

Export.mock_objects = Export.objects.db_manager('mock')
