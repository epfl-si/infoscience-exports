import factory
from django.contrib.auth.models import User

from exports.models import Export


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    name = factory.Iterator(['Name1', 'Name2'])


class AdminUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = 'admin'
    email = 'admin@localhost'
    password = factory.PostGenerationMethodCall('set_password', '1234')

    is_superuser = True
    is_staff = True
    is_active = True
