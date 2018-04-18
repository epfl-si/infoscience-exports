from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # sciper not necessarily an integer, could contain letters for a service account
    sciper = models.CharField(max_length=100, null=True, blank=True)
    where = models.CharField(max_length=100, null=True, blank=True)
    units = models.TextField(null=True, blank=True)
    group = models.TextField(null=True, blank=True)
    classe = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=100, null=True, blank=True)

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
                "statut:{0.statut}>").format(self)
