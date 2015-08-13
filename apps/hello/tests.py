# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from datetime import date

from .models import Person, RequestStore
from .views import home_page


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
        self.assertEquals(only_person, person)

        # and check that it's saved its two attributes: name and surname
        self.assertEquals(only_person.name, 'Aleks')
        self.assertEquals(only_person.surname, 'Woronow')


class HomePageTest(TestCase):
    def test_home_page(self):
        """Test root url resolves to home_page view"""
        found = resolve('/')
        self.assertEqual(found.func.func_name, home_page.func_name)

    def test_home_page_returns_correct_html(self):
        """Test home_page returns correct html"""
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.strip().
                        startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Site Name</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))


class RequestStoreTest(TestCase):
    def test_request_store(self):
        """Test creating a new request and saving it to the database"""
        request_store = RequestStore()
        request_store.path = '/'
        request_store.metod = 'GET'
        
        # check we can save it to the database
        request_store.save()
        
        # now check we can find it in the database again
        all_requests = RequestStore.objects.all()
        self.assertEquals(len(all_requests), 2)
        only_request = all_persons[0]
        self.assertEquals(only_request, request_store)

        # and check that it's saved its two attributes: path and method
        self.assertEquals(only_request.path, '/')
        self.assertEquals(only_request.method, 'GET')


class RequestMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestMiddle()
        self.user = get_user_model().objects.create(username="admin",
                                                    email="admin@i.ua",
                                                    password="admin")

    def test_middleware(self):
        """Test middleware RequestMiddle."""

        # middleware don't store request to page that show request
        request = self.factory.get(reverse('hello:request'))
        
        # if user logged-in
        request.user = self.user
        self.middleware.process_request(request)
        rs = RequestStore.objects.all()
        self.assertQuerysetEqual(rs, [])
        
        # if user is anonymous
        request.user = AnonymousUser()
        self.middleware.process_request(request)
        rs = RequestStore.objects.all()
        self.assertQuerysetEqual(rs, [])
        
        # middleware don't store request to ajax request
        request = self.factory.get(reverse('hello:request_ajax'))
        
        # if user logged-in
        request.user = self.user
        self.middleware.process_request(request)
        rs = RequestStore.objects.all()
        self.assertQuerysetEqual(rs, [])
        
        # if user is anonymous
        request.user = AnonymousUser()
        self.middleware.process_request(request)
        rs = RequestStore.objects.all()
        self.assertQuerysetEqual(rs, [])
        
        
        # middleware stores request to other pages 
        request = self.factory.get(reverse('hello:home'))

         # if user logged-in
        request.user = self.user
        self.middleware.process_request(request)
        rs = RequestStore.objects.get(path="/")
        self.assertEqual(rs.method, 'GET')
        self.assertEqual(rs.user, request.user)
        
        