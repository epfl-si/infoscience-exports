import factory
from exports.models import Export, User


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "User %03d" % n)
    email = factory.Sequence(lambda n: "test_user_%03d@nowhere.com" % n)
    password = factory.PostGenerationMethodCall('set_password', '1234')


class AdminUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = 'admin'
    email = 'admin@localhost'
    password = factory.PostGenerationMethodCall('set_password', '1234')

    is_superuser = True
    is_staff = True
    is_active = True


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    user = factory.SubFactory(UserFactory)
    name = factory.Iterator(['Name1', 'Name2'])
    url = 'https://infoscience.epfl.ch/search?ln=en&p=article&f=&sf=&so=d&rg=10'
    groupsby_type = 'NONE'
    groupsby_year = 'NONE'
    groupsby_doc = 'NONE'
    bullets_type = 'NONE'
    # created_at = factory.fuzzy.FuzzyDateTime
    # updated_at = factory.fuzzy.FuzzyDateTime


@factory.use_strategy(factory.BUILD_STRATEGY)
class ExportInMemoryFactory(ExportFactory):
    pass
