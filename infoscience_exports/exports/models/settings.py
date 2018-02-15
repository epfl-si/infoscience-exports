"""
Abstract classes, mainly used to avoid the one big model

"""

from django.db import models


class BaseSettings(models.Model):
    class Meta:
        abstract = True


class BulletsSettings(BaseSettings):
    BULLETS_TYPE_CHARACTER = 'C'
    BULLETS_TYPE_NUMBER = 'N'
    BULLETS_TYPE_CHOICE = (
        (BULLETS_TYPE_CHARACTER, 'Character'),
        (BULLETS_TYPE_NUMBER, 'Number'),
    )

    BULLETS_ORDER_ASCENDING = '+'
    BULLETS_ORDER_DESCENDING = '-'
    BULLETS_ORDER_CHOICE = (
        (BULLETS_ORDER_ASCENDING, 'Ascending'),
        (BULLETS_ORDER_DESCENDING, 'Descending'),
    )

    bullets_type = models.CharField(max_length=1,
                                    choices=BULLETS_TYPE_CHOICE,
                                    null=True,
                                    )
    bullets_text = models.CharField(max_length=5,
                                    null=True,
                                    )
    bullets_order = models.CharField(max_length=1,
                                     choices=BULLETS_ORDER_CHOICE,
                                     default=BULLETS_ORDER_ASCENDING,
                                     null=True,
                                     )

    class Meta:
        abstract = True
