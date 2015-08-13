# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from selenium import webdriver
from pyvirtualdisplay import Display


class HelloTest(LiveServerTestCase):
    def setUp(self):
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()
        self.display.stop()

    def test_load_initial_data(self):
        """Test load initial data"""

        # Gertrude opens her web browser, and goes to the home page
        self.browser.get(self.live_server_url)

        # She sees the familiar 'Aleks'
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Aleks', body.text)

    def test_can_request_page_receive_data_by_ajax(self):
        """Test can request page receive data by ajax"""

        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.live_server_url + '/admin/')

        # than to the request page
        self.browser.get(self.live_server_url + reverse('hello:request'))

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('admin', body.text)
