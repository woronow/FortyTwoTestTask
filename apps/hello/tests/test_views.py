# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.http import HttpRequest

from ..models import Person
from ..views import home_page


class HomePageViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.person = Person.objects.first()

    def test_home_page_view(self):
        """Test view home_page"""
        request = self.factory.get(reverse('hello:home'))
        response = home_page(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn(self.person.name, response.content)


class HomePageTest(TestCase):
    def test_home_page(self):
        """Test home page"""

        response = self.client.get(reverse('hello:home'))

        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response,
                            '<h1>42 Coffee Cups Test Assignmen</h1>',
                            html=True)
        self.assertContains(response, 'Aleks')
        self.assertContains(response, 'Woronow')
        self.assertContains(response, 'Aug. 12, 2015')
        self.assertContains(response, 'aleks.woronow@yandex.ru')
        self.assertContains(response, '42cc@khavr.com')
        self.assertContains(response, 'I was born ...')

    def test_home_page_returns_correct_html(self):
        """Test home page returns correct html"""
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.strip().
                        startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Visiting Card</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))


class RequestAjaxTest(TestCase):
    def test_request_ajax_view(self):

        """Test request ajax view"""
        response = self.client.get(reverse('hello:home'))
        response = self.client.get(reverse('hello:request_ajax'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIn('method', response.content)
        self.assertIn('GET', response.content)
        self.assertIn('path', response.content)
        self.assertIn('/', response.content)


class RequestViewTest(TestCase):
    def test_request_view(self):
        """Test request_view view"""

        response = self.client.get(reverse('hello:request'))

        self.assertTemplateUsed(response, 'request.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            '<h1>42 Coffee Cups Test Assignmen</h1>',
                            html=True)


class FormPageTest(TestCase):
    def test_form_page_view(self):
        """Test view form_page"""
        response = self.client.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:form'))
        self.assertIn('name', response.content)
