from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # sciper not necessarily an integer, could contain letters for a service account
    sciper = models.CharField(max_length=100, null=True, blank=True)
    where = models.CharField(max_length=100, null=True, blank=True)
    units = models.CharField(max_length=300, null=True, blank=True)
    group = models.CharField(max_length=4096, null=True, blank=True)
    classe = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)
    memberof = models.CharField(max_length=1024, null=True, blank=True)

    @property
    def profile(self):
        """ Work around current implementation of DjangoTequilla which expects to have all Tequila
            attributes in a profile object"""
        return self

    def __str__(self):
        if self.email:
            return self.email
        else:
            return self.username

    def __unicode__(self):
        return ("<Profile Sciper:{0.sciper} - "
                "where: {0.where} - "
                "units: {0.units} - "
                "group: {0.group} - "
                "classe:{0.class} - "
                "statut:{0.statut} - "
                "statut:{0.memberof}>").format(self)

    def nb_exports(self):
        return self.export_set.count()
