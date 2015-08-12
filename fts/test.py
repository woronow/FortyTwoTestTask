# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
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
