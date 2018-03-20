import socket
from urllib.parse import quote

from django.conf import settings
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from exports.test.factories import ExportInMemoryFactory
from exports.models import User, Export


@override_settings(ALLOWED_HOSTS=['*'])  # Open ALLOW_HOSTS
@override_settings(DEBUG=True)
class SeleniumStaticLiveServerTestCase(StaticLiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running Selenium.
    You can use a VNC client on localhost:5900 (password: secret)
    to get a view of the process
    """
    host = '0.0.0.0'  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set host to externally accessible web server address
        cls.host = socket.gethostbyname(socket.gethostname())

        cls.remote_selenium_address = getattr(settings, 'REMOTE_SELENIUM_SERVER', False)

        # Instantiate the remote WebDriver
        cls.selenium = webdriver.Remote(
            #  Set to: htttp://{selenium-container-name}:port/wd/hub
            #  In our example, the container is named `selenium`
            #  and runs on port 4444
            command_executor=cls.remote_selenium_address,
            # Set to CHROME since we are using the Chrome container
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        if cls.selenium:
            cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        """Open a new browser for each test."""
        super(SeleniumStaticLiveServerTestCase, self).setUp()

        test_user = User.objects.get_or_create(username='test',
                                               first_name='test',
                                               last_name='test',
                                               email='test@localhost',
                                               is_staff=True,
                                               is_active=True)[0]

        # # generate a cookie place, or get the cookie setting error from Chrome
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('not_allowed')))

        # bypass external Tequila auth
        self.client.force_login(test_user)

        # feed the cookie to selenium
        sessionid = self.client.cookies['sessionid']
        # add_cookie will be relative to this domain
        self.selenium.add_cookie({
            'name': 'sessionid',
            'value': sessionid.value,
            'secure': False,
            'path': '/'
        })

    def test_create(self):
        before_count = Export.objects.count()
        mpl = ExportInMemoryFactory()

        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('crud:export-create')))
        name_input = self.selenium.find_element_by_id("id_name")
        name_input.send_keys(mpl.name)
        url_input = self.selenium.find_element_by_id("id_url")
        url_input.send_keys(mpl.url)

        self.selenium.find_element_by_id("btn-submit").click()
        self.assertGreater(Export.objects.count(), before_count)

    def test_url_as_paramter_will_autofill_form(self):
        full_url = '%s%s' % (self.live_server_url,
                             reverse('crud:export-create'))
        infoscience_url = 'https://infoscience.epfl.ch/search?ln=en&p=vetterli' \
                          '&f=&c=Infoscience%2FArticle&c=Infoscience%2FReview&c=Infoscience%2FThesis' \
                          '&c=Infoscience%2FWorking+papers&c=Infoscience%2FProceedings' \
                          '&c=Infoscience%2FPresentation&c=Infoscience%2FPatent&c=Infoscience%2FStudent' \
                          '&c=Media&c=Other+doctypes&c=Infoscience%2FConference&c=Infoscience%2FReport' \
                          '&c=Infoscience%2FBook&c=Infoscience%2FChapter&c=Infoscience%2FPoster&c=Infoscience%2FStandard' \
                          '&c=Infoscience%2FLectures&c=Infoscience%2FDataset' \
                          '&c=Infoscience%2FPhysical+objects&c=Work+done+outside+EPFL' \
                          '&sf=&so=d&rg=10'

        awaited_result_url = 'https://infoscience.epfl.ch/search?ln=en&p=vetterli' \
                          '&f=&c=Infoscience/Article&c=Infoscience/Review&c=Infoscience/Thesis' \
                          '&c=Infoscience/Working+papers&c=Infoscience/Proceedings' \
                          '&c=Infoscience/Presentation&c=Infoscience/Patent&c=Infoscience/Student' \
                          '&c=Media&c=Other+doctypes&c=Infoscience/Conference&c=Infoscience/Report' \
                          '&c=Infoscience/Book&c=Infoscience/Chapter&c=Infoscience/Poster&c=Infoscience/Standard' \
                          '&c=Infoscience/Lectures&c=Infoscience/Dataset' \
                          '&c=Infoscience/Physical+objects&c=Work+done+outside+EPFL' \
                          '&sf=&so=d&rg=10'

        full_url = '{}?url={}'.format(full_url, quote(infoscience_url, safe=''))

        self.selenium.get(full_url)

        url_input = self.selenium.find_element_by_id("id_url").get_attribute("value")
        msg_on_fail = "Url is not the one we want : {}".format(url_input)
        self.assertEqual(url_input, awaited_result_url, msg=msg_on_fail)
