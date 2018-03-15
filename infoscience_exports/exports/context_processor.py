from django.conf import settings
from exports import __version__, __build__


def site_url(request):
    return {
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_PATH': settings.SITE_PATH,
        }


def version(request):
    return {
        'VERSION': __version__,
        'BUILD': __build__
        }
