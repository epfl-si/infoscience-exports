from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from .factories import ExportFactory, AdminUserFactory
from exports.models import Export


class APITestCase(TransactionTestCase):
    # reset_sequences = True

    def setUp(self):
        # fixtures
        (self.mpl, self.mi) = ExportFactory.create_batch(2)

        AdminUserFactory.create()
        self.client.login(username='admin', password='1234')

    def test_missing_name(self):
        as_before = Export.objects.count()

        response = self.client.post(reverse('api:export-list'),
                                    """
                                    {
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Export.objects.count(), as_before)

    def test_blank_name(self):
        as_before = Export.objects.count()

        response = self.client.post(reverse('api:export-list'),
                                    """
                                    {
                                        "name": "",
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Export.objects.count(), as_before)

    # - 1. GET /exports
    def test_get_exports(self):
        self.assertEqual(Export.objects.count(), 2)

        response = self.client.get(reverse('api:export-list'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "count": 2,
                                 "next": null,
                                 "previous": null,
                                 "results": [
                                     {
                                        "id": %s,
                                        "name": "Name1"
                                     },
                                     {
                                        "id": %s,
                                        "name": "Name2"
                                     }
                                 ]
                             }
                             """ % (self.mpl.pk, self.mi.pk,))

        self.assertEqual(Export.objects.count(), 2)

    # - 2. GET /exports/1
    def test_get_export_1(self):
        response = self.client.get(reverse('api:export-detail',
                                           args=[self.mpl.pk]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "Name1"
                             }
                             """ % (self.mpl.pk,))

    def test_get_export_1_doesnt_exist(self):
        pk = self.mpl.pk

        self.mpl.delete()

        response = self.client.get(reverse('api:export-detail',
                                           args=[pk]),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_export_invalid_pk(self):
        response = self.client.get(reverse('api:export-detail',
                                           args=['invalid_pk']),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    # - 3. POST /exports
    def test_post_export(self):
        before_count = Export.objects.count()

        response = self.client.post(reverse('api:export-list'),
                                    """
                                    {
                                        "name": "Toto"
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Export.objects.count(), before_count + 1)
        new_pk = Export.objects.get(name='Toto').pk

        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "Toto"
                             }
                             """ % (new_pk,))

    def test_post_export_invalid_payload(self):
        response = self.client.post(reverse('api:export-list'),
                                    """
                                    {
                                        name: "Not a valid payload
                                        &/())== at all !!!!,, []
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("JSON parse error" in response.data.get('detail'))

    def test_post_export_invalid_name(self):
        name_max_length = Export._meta.get_field('name').max_length
        too_long = 'x' * (name_max_length + 1)

        response = self.client.post(reverse('api:export-list'),
                                    """
                                    {
                                        "name": "%s"
                                    }
                                    """ % (too_long,),
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("no more than %s characters" % (name_max_length,)
                        in str(response.data.get('name')))

    # - 4. PUT /exports/1
    def test_put_export(self):
        before_count = Export.objects.count()

        pk = self.mpl.pk
        self.assertNotEqual(self.mpl.name, 'newName')

        response = self.client.put(reverse('api:export-detail',
                                           args=[pk]),
                                   """
                                   {
                                       "name": "newName"
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Export.objects.count(), before_count)
        self.assertTrue(Export.objects.get(name='newName'))

        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "newName"
                             }
                             """ % (pk,))

    def test_put_export_invalid_payload(self):
        response = self.client.put(reverse('api:export-detail',
                                           args=[self.mpl.pk]),
                                   """
                                   {
                                       name: "Not a valid payload
                                       &/())== at all !!!!,, []
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("JSON parse error" in response.data.get('detail'))

    def test_put_export_invalid_pk(self):
        response = self.client.put(reverse('api:export-detail',
                                           args=['invalid_pk']),
                                   """
                                   {
                                       "name": "newName"
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_put_export_invalid_name(self):
        name_max_length = Export._meta.get_field('name').max_length
        too_long = 'x' * (name_max_length + 1)

        response = self.client.put(reverse('api:export-detail',
                                           args=[self.mpl.pk]),
                                   """
                                   {
                                       "name": "%s"
                                   }
                                   """ % (too_long,),
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("no more than %s characters" % (name_max_length,)
                        in str(response.data.get('name')))

    # - 5. DELETE /exports/1
    def test_delete_export(self):
        pk = self.mpl.pk

        response = self.client.delete(reverse('api:export-detail',
                                              args=[self.mpl.pk]),
                                      follow=True)

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Export.DoesNotExist):
            Export.objects.get(id=pk)

    def test_delete_export_invalid_pk(self):
        before_count = Export.objects.count()

        response = self.client.delete(reverse('api:export-detail',
                                              args=['invalid_pk']),
                                      follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Export.objects.count(), before_count)
