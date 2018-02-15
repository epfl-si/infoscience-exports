from django.core.exceptions import ValidationError
from django.test import TransactionTestCase
from .factories import ExportFactory
from exports.models import Export


class ExportsTestCase(TransactionTestCase):
    def setUp(self):
        # fixtures
        (self.mpl, self.mi) = ExportFactory.create_batch(2)

    def test_unicode_representation(self):
        self.assertEqual(self.mpl.name, 'Name1')

    def test_export_creation(self):
        ExportFactory(name='This is a test')

        self.assertEqual(
            len(Export.objects.filter(name='This is a test')), 1)

    def test_missing_name(self):
        with self.assertRaises(Exception):
            ExportFactory(name=None)

    def test_blank_name(self):
        with self.assertRaises(ValidationError):
            ExportFactory.build(name='').full_clean()
