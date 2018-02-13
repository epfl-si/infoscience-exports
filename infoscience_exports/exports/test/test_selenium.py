from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.firefox.webdriver import WebDriver
from exports.models import Export


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(MySeleniumTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def test_create(self):
        name = 'name1'
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('crud:export-create')))
        name_input = self.selenium.find_element_by_id("id_name")
        name_input.send_keys(name)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        self.assertTrue(Export.objects.latest('id'))
