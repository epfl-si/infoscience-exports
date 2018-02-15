from django.test import TransactionTestCase
from django.urls import reverse
from .factories import ExportFactory
from ..models import Export


class ExportTest(TransactionTestCase):
    def setUp(self):
        self.mpl = ExportFactory()

    def test_factory_create(self):
        """
        Test that we can create an instance via our object factory.
        """
        self.assertTrue(isinstance(self.mpl, Export))

    def test_list_view(self):
        """
        Test that the list view returns at least our factory created instance.
        """
        response = self.client.get(reverse('crud:export-list'))
        object_list = response.context['object_list']
        self.assertIn(self.mpl, object_list)

    def test_create_view(self):
        """
        Test that we can create an instance via the create view.
        """
        new_name = 'Name1'
        total = Export.objects.count()

        response = self.client.post(reverse('crud:export-create'),
                                    data={'name': new_name}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(total + 1, Export.objects.count())
        self.assertTrue(Export.objects.filter(name=new_name).exists())

    def test_detail_view(self):
        """
        Test that we can view an instance via the detail view.
        """
        response = self.client.get(self.mpl.get_absolute_url())
        self.assertEqual(response.context['object'], self.mpl)

    def test_update_view(self):
        """
        Test that we can update an instance via the update view.
        """
        update_name = 'export_updated'
        pk = self.mpl.pk

        with self.assertRaises(Export.DoesNotExist):
            Export.objects.get(name=update_name)

        response = self.client.post(reverse('crud:export-update',
                                            kwargs={'pk': pk, }),
                                    data={'name': update_name},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Export.objects.get(name=update_name))

    def test_delete_view(self):
        """
        Test that we can delete an instance via the delete view.
        """
        pk = self.mpl.pk
        response = self.client.post(reverse('crud:export-delete',
                                            kwargs={'pk': pk, }),
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Export.objects.filter(pk=pk).exists())
