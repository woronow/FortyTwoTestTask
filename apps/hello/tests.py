# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from .decorators import not_record_request

from datetime import date

from .models import Person, RequestStore
from .views import home_page
from apps.middleware.helloRequest import RequestMiddle


class PersonModelTests(TestCase):
    def test_person(self):
        """Test creating a new person and saving it to the database"""
        person = Person()
        person.name = 'Aleks'
        person.surname = 'Woronow'
        person.date_of_birth = date(2105, 7, 14)
        person.bio = 'I wasborn ...'
        person.email = 'akeks.woronow@yandex.ru'
        person.jabber = '42cc@khavr.com'
        person.skype_id = ''
        person.other = ''

        # check we can save it to the database
        person.save()

        # now check we can find it in the database again
        all_persons = Person.objects.all()
        self.assertEquals(len(all_persons), 2)
        only_person = all_persons[1]
        self.assertEquals(str(only_person), str(person))

        # and check that it's saved its two attributes: name and surname
        self.assertEquals(only_person.name, 'Aleks')
        self.assertEquals(only_person.surname, 'Woronow')


class HomePageTest(TestCase):
    def test_home_page(self):
        """Test home page"""
        c = Client()
        response = c.get(reverse('hello:home'))

        person = Person.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['person'], person)

    def test_home_page_returns_correct_html(self):
        """Test home_page returns correct html"""
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.strip().
                        startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Visiting Card</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))


class RequestStoreTest(TestCase):
    def test_request_store(self):
        """Test creating a new request and saving it to the database"""
        request_store = RequestStore()
        request_store.path = '/'
        request_store.method = 'GET'

        # check we can save it to the database
        request_store.save()

        # now check we can find it in the database again
        all_requests = RequestStore.objects.all()
        self.assertEquals(len(all_requests), 1)
        only_request = all_requests[0]
        self.assertEquals(str(only_request), str(request_store))

        # and check that it's saved its two attributes: path and method
        self.assertEquals(only_request.path, '/')
        self.assertEquals(only_request.method, 'GET')


class RequestMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.middleware = RequestMiddle()
        self.request_store = RequestStore
        self.user = get_user_model().objects.get(id=1)

    def test_middleware_is_included(self):
        """Test for inclusion RequestMiddleware in project"""
        self.client.get(reverse('hello:home'))
        last_middleware_obj = self.request_store.objects.last()
        self.assertEqual(last_middleware_obj.method, 'GET')
        self.assertEqual(last_middleware_obj.path, reverse('hello:home'))

    def test_middleware(self):
        """Test middleware RequestMiddle."""
        request = self.factory.get(reverse('hello:home'))

        # middleware don't store request to decorated function
        decorated_func = not_record_request(home_page)
        request.user = self.user
        self.middleware.process_view(request,  decorated_func)
        rs = RequestStore.objects.all()
        self.assertQuerysetEqual(rs, [])

        # middleware store request to undecorated function
        request.user = self.user
        self.middleware.process_view(request, home_page)
        rs = self.request_store.objects.all()
        self.assertEquals(len(rs), 1)
        only_one_rs = rs[0]
        self.assertEqual(only_one_rs.path, reverse('hello:home'))

        # if user is anonymous
        request.user = AnonymousUser()
        self.middleware.process_view(request, home_page)
        rs = self.request_store.objects.all()
        self.assertEquals(len(rs), 2)
        only_one_rs = rs[1]
        self.assertEqual(only_one_rs.path, reverse('hello:home'))


class RequestAjaxTest(TestCase):
    def test_request_ajax_view(self):
        """Test request ajax view"""
        RequestStore.objects.create(path='/', method='GET')
        c = Client()
        response = c.get(reverse('hello:request_ajax'),
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIn('GET', response.content)


class HomePageViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.person = Person.objects.first()

    def test_home_page_view(self):
        """Test view home_page"""
        request = self.factory.get(reverse('hello:home'))
        response = home_page(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.person.name, response.content)
