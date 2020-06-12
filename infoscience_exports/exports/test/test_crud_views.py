from pathlib import Path
from lxml.html.diff import htmldiff

from django.test import TransactionTestCase
from django.urls import reverse

from .factories import ExportFactory, ExportInMemoryFactory
from ..models import Export


class ExportTest(TransactionTestCase):
    def setUp(self):
        self.mpl = ExportFactory()

        export_for_data = ExportInMemoryFactory()
        self.export_data_to_post = {
            'name': export_for_data.name,
            'url': export_for_data.url,
            'groupsby_type': export_for_data.groupsby_type,
            'groupsby_year': export_for_data.groupsby_year,
            'groupsby_doc': export_for_data.groupsby_doc,
            'bullets_type': export_for_data.bullets_type,
            'formats_type': export_for_data.formats_type,
        }

    def test_factory_create(self):
        """
        Test that we can create an instance via our object factory.
        """
        self.assertTrue(isinstance(self.mpl, Export))

    def test_list_view(self):
        """
        Test that the list view returns at least our factory created instance.
        """
        self.client.force_login(self.mpl.user)
        response = self.client.get(reverse('crud:export-list'))
        object_list = response.context['object_list']
        self.assertIn(self.mpl, object_list, "{}".format(response))

    def test_create_view(self):
        """
        Test that we can create an instance via the create view.
        """
        new_name = 'Name1'
        total = Export.objects.count()

        self.client.force_login(self.mpl.user)
        response = self.client.post(reverse('crud:export-create'),
                                    data=self.export_data_to_post,
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(total + 1, Export.objects.count(), "{}".format(response.content))
        self.assertTrue(Export.objects.filter(name=new_name).exists())

    def test_detail_view(self):
        """
        Test that we can view an instance via the detail view.
        """
        response = self.client.get(self.mpl.get_absolute_url())
        self.assertEqual(response.context['object'], self.mpl)

    def test_update_deny_without_log_view(self):
        """
        Test that we can not update a export without being logged
        """
        pk = self.mpl.pk

        response = self.client.post(reverse('crud:export-update', kwargs={'pk': pk, }),
                                    data=self.export_data_to_post,
                                    follow=True)

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 403)

    def test_update_view(self):
        """
        Test that we can update an instance via the update view.
        """
        update_name = 'export_updated'
        pk = self.mpl.pk

        with self.assertRaises(Export.DoesNotExist):
            Export.objects.get(name=update_name)

        self.client.force_login(self.mpl.user)
        response = self.client.post(reverse('crud:export-update', kwargs={'pk': pk, }),
                                    data=self.export_data_to_post,
                                    follow=True)

        self.assertEqual(response.status_code, 200)

    def test_delete_deny_without_log_view(self):
        """
        Test that we can delete an instance via the delete view.
        """
        pk = self.mpl.pk
        response = self.client.post(reverse('crud:export-delete', kwargs={'pk': pk, }),
                                    follow=True)

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Export.objects.filter(pk=pk).exists())

    def test_delete_view(self):
        """
        Test that we can delete an instance via the delete view.
        """
        pk = self.mpl.pk
        self.client.force_login(self.mpl.user)
        response = self.client.post(reverse('crud:export-delete', kwargs={'pk': pk, }),
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Export.objects.filter(pk=pk).exists())


class ExportRenderTest(TransactionTestCase):
    def setUpExport(self, url='https://infoscience.epfl.ch/search?as=1&fieldrestriction=any&ln=en&of=xm&p=037__a%3A%27ARTICLE%27&rg=12&sf=year&so=d'):
        #'https://infoscience.epfl.ch/search?ln=en&p=article&f=&sf=&so=d&rg=10'
        self.url = url
        self.mpl = ExportFactory(url=url,
                                 formats_type="SHORT",
                                 groupsby_type="DOC_TITLE",
                                 groupsby_year="YEAR_TITLE",
                                 show_linkable_authors=True
                                 )

        pk = self.mpl.pk
        self.client.force_login(self.mpl.user)

        response = self.client.get(reverse('crud:export-view', kwargs={'pk': pk, }))
        self.assertEqual(response.status_code, 200)
        self.rendered_html = response.content.decode("utf-8")

        # for debugging porpose, better write down the file
        export_html_file = Path(__file__).resolve().parent / "html" / "export_rendered.html"
        export_html_file.write_text(self.rendered_html)

    def setUp(self):
        self.setUpExport()

    def test_limit_is_applied(self):
        self.assertIn("&rg=2", self.url)
        self.assertEqual(self.rendered_html.count('<div class="row">'), 2)

    def test_new_render_view(self):
        """
        Test final html rendered by comparing with a reference file.
        Write the result into ./rendered/export.html
        """
        ref_render_html = (Path(__file__).resolve().parent / 'new_ref_render.html').read_text()

        self.longMessage = False
        self.assertEqual(
            ref_render_html,
            self.rendered_html,
            htmldiff(ref_render_html, self.rendered_html)
        )
        self.longMessage = True

        assert False
