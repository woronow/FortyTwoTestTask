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

from datetime import date

from .models import Person, RequestStore
from .forms import PersonForm
from .views import home_page
from .decorators import not_record_request
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

        # check photo size maintaining aspect ratio
        size_photo = only_person.gauge_height()
        self.assertEqual(size_photo['h'], 200)


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
        """Test request_ajax view"""
        RequestStore.objects.create(path='/', method='GET')
        c = Client()
        response = c.get(reverse('hello:request_ajax'),
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIn('GET', response.content)
        self.assertEqual(response.status_code, 200)


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


class FormTest(TestCase):
    def test_form(self):
        """Test form"""
        form_data = {'name': '',
                     'surname': 'Woronow',
                     'date_of_birth': date(2105, 7, 14),
                     'email': 'aleks.woronow@yandex.ru',
                     'jabber': '42cc@khavr.com'}
        form = PersonForm(data=form_data)

        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors['name'], ['This field is required.'])

        form_data['name'] = 'Aleks'
        form = PersonForm(data=form_data)

        self.assertEqual(form.is_valid(), True)

    def test_form_page_view(self):
        """Test view form_page"""
        c = Client()
        response = c.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 302)

        c.login(username='admin', password='admin')
        response = c.get(reverse('hello:form'))
        self.assertIn('name', response.content)


class CommandsTestCase(TestCase):
    def test_showmodels(self):
        " Test showmodels command."
        out = StringIO()
        call_command('showmodels', stdout=out, stderr=out)
        self.assertIn('Person - 0', out.getvalue())
        self.assertIn('error:', out.getvalue())
        
        Person.objects.create(name='Aleks',
                              surname='Woronow',
                              date_of_birth=date(2105, 7, 14),
                              email='hello@i.ua',
                              jabber='42cc@khavr.com')
        call_command('showmodels', stdout=out, stderr=out)
        self.assertIn('Person - 1', out.getvalue())
                      