from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.conf import settings

from dirtyfields import DirtyFieldsMixin


class Export(DirtyFieldsMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             )
    name = models.CharField(max_length=50, blank=False, null=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('crud:export-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-id']

Export.mock_objects = Export.objects.db_manager('mock')


# Temp placement, it will move after merge
class User(AbstractUser):
    sciper = models.PositiveIntegerField(null=True, blank=True)
    where = models.CharField(max_length=100, null=True, blank=True)
    units = models.CharField(max_length=300, null=True, blank=True)
    group = models.CharField(max_length=150, null=True, blank=True)
    classe = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return """  Sciper:    %s
                        where:     %s
                        units:     %s
                        group:     %s
                        classe:    %s
                        statut:    %s
                        memberof:  %s
                    """ % (self.sciper,
                           self.where,
                           self.units,
                           self.group,
                           self.classe,
                           self.statut,
                           self.memberof)
