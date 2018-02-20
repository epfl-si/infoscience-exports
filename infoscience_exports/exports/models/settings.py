"""
Abstract classes, mainly used to avoid the one big model

"""

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
        ('', ''),
        ('CHARACTER_STAR', '*'),
        ('CHARACTER_MINUS', '-'),
        ('NUMBER_ASC', '1, 2, 3, ...'),
        ('NUMBER_DESC', '..., 3, 2, 1'),
    )

    bullets_type = models.CharField(max_length=255,
                                    choices=BULLETS_TYPE_CHOICE,
                                    null=True
                                    )

    class Meta:
        abstract = True
