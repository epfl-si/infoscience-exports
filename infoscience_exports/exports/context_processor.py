from django.conf import settings


def site_url(request):
    return {
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_PATH': settings.SITE_PATH,
        }
