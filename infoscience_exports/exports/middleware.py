from django.utils import translation
from django.conf import settings
from django.urls import resolve


class InvenioLocaleMiddleware:
    """ Respect the Invenio way on setting the language"""

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if 'ln' in request.GET:
            language = request.GET['ln']
        elif request.session.get(settings.LANGUAGE_SESSION_KEY):
            language = request.session[settings.LANGUAGE_SESSION_KEY]
        else:
            language = settings.LANGUAGE_CODE

        if language != translation.get_language():  # is this different from current?
            translation.activate(language)
            request.LANGUAGE_CODE = language

            # don't save into sessions when only viewing a list of publication
            if resolve(request.path_info).url_name != 'export-view':
                request.session[settings.LANGUAGE_SESSION_KEY] = language

        response = self.get_response(request)
        return response
