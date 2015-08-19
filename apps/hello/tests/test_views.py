# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.core.management import call_command
from django.utils.six import StringIO

from ..models import Person
from ..views import home_page
from ..decorators import not_record_request


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
        """Test home_page returns correct html"""
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.strip().
                        startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Visiting Card</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))


class RequestAjaxTest(TestCase):
    def test_request_ajax_view(self):
        """Test request_ajax view"""
        RequestStore.objects.create(path='/', method='GET')
        c = Client()
        response = c.get(reverse('hello:request_ajax'),
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIn('GET', response.content)
        self.assertEqual(response.status_code, 200)


class RequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_store = RequestStore

    def test_request_view(self):
        """Test view request_view"""

        # middleware don't store request to request_view page
        response = self.client.get(reverse('hello:request'))
        all_store_obj = self.request_store.objects.all()
        self.assertQuerysetEqual(all_store_obj, [])
        self.assertEqual(response.status_code, 200)
        self.assertIn('Requests', response.content)

        # middleware store request to home_page page
        response = self.client.get(reverse('hello:home'))
        all_store_obj = self.request_store.objects.all()
        store_obj = all_store_obj[0]
        self.assertEqual(len(all_store_obj), 1)
        self.assertEqual(store_obj.path, reverse('hello:home'))
        self.assertEqual(store_obj.new_request, 1)

        # new_request fields update to 0, if request_page is requested by admin
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:request'))
        all_store_obj = self.request_store.objects.all()
        store_obj = all_store_obj[0]
        self.assertEqual(len(all_store_obj), 1)
        self.assertEqual(store_obj.new_request, 0)
