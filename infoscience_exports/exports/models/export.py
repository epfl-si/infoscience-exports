import os

from django.urls import reverse
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.core.cache import cache
from django.utils.safestring import mark_safe

from auditlog.registry import auditlog
from dirtyfields import DirtyFieldsMixin

from .settings import BulletsSettings, ThumbnailSettings, LinksSettings, \
    GroupBySettings, PendingPublicationsSettings, FormatsSettings, LimitSettings, \
    AdvancedOptionsSettings, SummarySettings


class Export(BulletsSettings,
             ThumbnailSettings,
             SummarySettings,
             LinksSettings,
             GroupBySettings,
             PendingPublicationsSettings,
             FormatsSettings,
             LimitSettings,
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

    SERVER_ENGINE_CHOICES = {
        ('invenio', "invenio"),
        ('dspace', "dspace"),
    }

    # save if the data for this export come from Invenio or Dspace
    server_engine = models.CharField(
        max_length=10,
        choices=SERVER_ENGINE_CHOICES,
        blank=True
    )

    # The rendered page is saved into this. This mechanism is here as we may move away from Invenio, so some export
    # may not be able to crawl again the data. In that case, it should use this.
    last_rendered_page = models.TextField(
        editable=False,
        default=None,
        null=True
    )
    last_rendered_page_usage_at = models.DateTimeField(
        editable=False,
        default=None,
        null=True
    )

    def __str__(self):
        return "Export {} {}".format(self.id, self.name)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return

        # set the correct engine name when creating new exports.
        # There is no safe way to tell which one is right.
        # So the default one is written into an env. variable.
        # Default being 'dspace'.
        current_server_engine = os.environ.get('SERVER_ENGINE', 'dspace')
        instance.server_engine = current_server_engine
        instance.save()

    def get_absolute_url(self):
        return reverse('crud:export-view', args=[str(self.id)])

    def get_cache_key_for_view(self, language):
        """ build an uniq key per object for the view"""
        return "view_export_{}_{}".format(self.id, language)

    class Meta:
        ordering = ['-id']


post_save.connect(Export.post_create, sender=Export)


class LegacyExport(models.Model):
    """
    Old exports that were imported
    """
    ORIGIN_CHOICE = (
        ('OTHER', ''),
        ('JAHIA', 'Jahia'),
        ('PEOPLE', 'People'),
    )

    export = models.ForeignKey(
        Export,
        on_delete=models.CASCADE
    )

    # allow null as we may not have an export
    legacy_id = models.IntegerField(blank=True, null=True)
    legacy_url = models.TextField()
    language = models.TextField()
    referenced_url = models.TextField()  # the page that use this export
    origin = models.TextField(choices=ORIGIN_CHOICE)
    origin_sciper = models.TextField()
    origin_id = models.TextField()
    raw_csv_entry = models.TextField()
    content_delta = models.IntegerField(blank=True, null=True)  # diff between old system and new

    def __str__(self):
        return "{} ({})".format(self.legacy_url, self.origin)

    def get_with_langage_absolute_url(self):
        """ get the url of the export, and add the language needed"""
        return reverse('crud:export-view', args=[str(self.export.id)]) + '?ln={}'.format(self.language)

    def link_to_old_export(self):
        from exporter.models import SettingsManager
        id = SettingsManager.get_legacy_export_id_from_url(self.legacy_url)
        if id:
            return mark_safe('<a target="_blank" href='
                             '"https://test-infoscience.epfl.ch/curator/export/{}/edit/">'
                             'see on old site</a>'.format(id))
        else:
            return "Not available"


def invalidate_view_cache(sender, instance, **kwargs):
    """ invalidate cache for installed languages"""
    languages = settings.LANGUAGES

    for lang in languages:
        ln = lang[0]
        cache_key = instance.get_cache_key_for_view(ln)

        if cache_key in cache:
            cache.delete(cache_key)


post_save.connect(invalidate_view_cache, sender=Export)
auditlog.register(Export)
