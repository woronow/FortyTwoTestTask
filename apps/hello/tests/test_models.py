# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from datetime import date

from ..models import Person, RequestStore, NoteModel
from ..forms import PersonForm
from apps.middleware.helloRequest import RequestMiddle

class PersonModelTests(TestCase):
    def test_person_model(self):
        """Test creating a new person and saving it to the database"""
        person = Person()

        # test model blank and null fields validation
        try:
            person.full_clean()
        except ValidationError as err:
            self.assertEquals(err.message_dict['name'][0],
                              Person._meta.get_field('name').
                              error_messages['blank'])
            self.assertEquals(err.message_dict['surname'][0],
                              Person._meta.get_field('surname').
                              error_messages['blank'])
            self.assertEquals(err.message_dict['email'][0],
                              Person._meta.get_field('email').
                              error_messages['blank'])
            self.assertEquals(err.message_dict['date_of_birth'][0],
                              Person._meta.get_field('date_of_birth').
                              error_messages['null'])

        # test model email and date field validation
        person.email = 'aleks@'
        person.jabber = '42cc'
        person.date_of_birth = 'sd'
        try:
            person.full_clean()
        except ValidationError as err:
            self.assertEquals(err.message_dict['email'][0],
                              EmailValidator.message)
            self.assertEquals(err.message_dict['jabber'][0],
                              EmailValidator.message)
            self.assertIn(Person._meta.get_field('date_of_birth').
                          error_messages['invalid'].format()[12:],
                          err.message_dict['date_of_birth'][0])

        # test cretae and save object
        person.name = 'Aleks'
        person.surname = 'Woronow'
        person.date_of_birth = date(2105, 7, 14)
        person.bio = 'I was born ...'
        person.email = 'aleks.woronow@yandex.ru'
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
        self.assertEquals(only_person.bio, 'I was born ...')
        self.assertEquals(str(only_person), 'Woronow Aleks')
        
        # check photo size maintaining aspect ratio
        size_photo = only_person.gauge_height()
        self.assertEqual(size_photo['h'], 200)


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
        self.assertIn('Person - 1', out.getvalue())
        self.assertIn('error:', out.getvalue())

        Person.objects.create(name='Ivan',
                              surname='Ivanov',
                              date_of_birth=date(2105, 7, 14),
                              email='hello@i.ua',
                              jabber='42cc@khavr.com')
        call_command('showmodels', stdout=out, stderr=out)
        self.assertIn('Person - 2', out.getvalue())


class NoteModelTestCase(TestCase):
    def test_processor(self):
        " Test processor."
        note = NoteModel.objects.get(model='Person')
        self.assertEqual(note.action_type, 0)