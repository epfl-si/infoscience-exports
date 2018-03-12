"""
Abstract classes, mainly used to avoid the one big model

"""

from django.utils.translation import ugettext_lazy as _
from django.db import models


class BaseSettings(models.Model):
    class Meta:
        abstract = True


class ThumbnailSettings(BaseSettings):
    show_thumbnail = models.BooleanField(default=False)

    class Meta:
        abstract = True


class BulletsSettings(BaseSettings):
    BULLETS_TYPE_CHOICE = (
        ('NONE', ''),
        ('CHARACTER_STAR', '*'),
        ('CHARACTER_MINUS', '-'),
        ('NUMBER_ASC', '1, 2, 3, ...'),
        ('NUMBER_DESC', '..., 3, 2, 1'),
    )

    bullets_type = models.CharField(
        max_length=255,
        choices=BULLETS_TYPE_CHOICE,
        default='NONE'
    )

    class Meta:
        abstract = True


class LinksSettings(BaseSettings):
    show_linkable_titles = models.BooleanField(default=False)
    show_linkable_authors = models.BooleanField(default=False)
    show_links_for_printing = models.BooleanField(default=False)
    show_detailed = models.BooleanField(default=True)
    show_fulltext = models.BooleanField(default=True)
    show_viewpublisher = models.BooleanField(default=True)

    class Meta:
        abstract = True


class GroupBySettings(BaseSettings):
    GROUPSBY_YEAR_CHOICE = (
        ('NONE', ''),
        ('YEAR_TITLE', _('year as title')),
    )

    GROUPSBY_DOC_CHOICE = (
        ('NONE', ''),
        ('DOC', _('document type')),
        ('DOC_TITLE', _('document type as title')),
    )

    GROUPSBY_ALL_CHOICE = (
        ('NONE', ''),
        ('YEAR_TITLE', _('year as title')),
        ('DOC', _('document type')),
        ('DOC_TITLE', _('document type as title')),
    )

    groupsby_type = models.CharField(
        max_length=255,
        choices=GROUPSBY_ALL_CHOICE,
        default='NONE'
    )

    groupsby_year = models.CharField(
        max_length=255,
        choices=GROUPSBY_YEAR_CHOICE,
        default='NONE'
    )

    groupsby_doc = models.CharField(
        max_length=255,
        choices=GROUPSBY_DOC_CHOICE,
        default='NONE'
    )

    class Meta:
        abstract = True


class PendingPublicationsSettings(BaseSettings):
    show_pending_publications = models.BooleanField(default=False)

    class Meta:
        abstract = True


class FormatsSettings(BaseSettings):
    FORMATS_TYPE_CHOICE = (
        ('SHORT', _('short')),
        ('DETAILED', _('detailed')),
    )

    formats_type = models.CharField(
        max_length=255,
        choices=FORMATS_TYPE_CHOICE,
        default='SHORT'
    )

    class Meta:
        abstract = True
