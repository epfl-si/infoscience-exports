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
        ('DOC_TITLE', _('document type as title')),
    )

    GROUPSBY_ALL_CHOICE = (
        ('NONE', ''),
        ('YEAR_TITLE', _('year as title')),
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


class AdvancedOptionsSettings(BaseSettings):
    show_article_volume = models.BooleanField(default=False)
    show_article_volume_number = models.BooleanField(default=False)
    show_article_volume_pages = models.BooleanField(default=False)
    show_thesis_directors = models.BooleanField(default=False)
    show_thesis_pages = models.BooleanField(default=False)
    show_report_working_papers_pages = models.BooleanField(default=False)
    show_conf_proceed_place = models.BooleanField(default=False)
    show_conf_proceed_date = models.BooleanField(default=False)
    show_conf_paper_journal_name = models.BooleanField(default=False)
    show_book_isbn = models.BooleanField(default=False)
    show_book_doi = models.BooleanField(default=False)
    show_book_chapter_isbn = models.BooleanField(default=False)
    show_book_chapter_doi = models.BooleanField(default=False)
    show_patent_status = models.BooleanField(default=False)

    class Meta:
        abstract = True
