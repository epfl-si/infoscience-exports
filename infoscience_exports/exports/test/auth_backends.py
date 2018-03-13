from exports.models import User


class TestcaseUserBackend(object):
    """ Bypass any authentication """
    def authenticate(self, request, test_user):
        return test_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
