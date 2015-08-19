# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model

from datetime import date

from ..models import Person, RequestStore, NoteModel


class PersonModelTests(TestCase):
    def test_person_model(self):
        """Test creating a new person and saving it to the database"""
        person = Person()

        # test model blank and null fields validation
        with self.assertRaises(ValidationError) as err:
            person.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(err_dict['name'][0],
                          Person._meta.get_field('name').
                          error_messages['blank'])
        self.assertEquals(err_dict['surname'][0],
                          Person._meta.get_field('surname').
                          error_messages['blank'])
        self.assertEquals(err_dict['email'][0],
                          Person._meta.get_field('email').
                          error_messages['blank'])
        self.assertEquals(err_dict['date_of_birth'][0],
                          Person._meta.get_field('date_of_birth').
                          error_messages['null'])

        # test model email and date field validation
        person.email = 'aleks@'
        person.jabber = '42cc'
        person.date_of_birth = 'sd'
        with self.assertRaises(ValidationError) as err:
            person.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(err_dict['email'][0],
                          EmailValidator.message)
        self.assertEquals(err_dict['jabber'][0],
                          EmailValidator.message)
        self.assertIn(Person._meta.get_field('date_of_birth').
                      error_messages['invalid'].format()[12:],
                      err_dict['date_of_birth'][0])

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

        user = get_user_model().objects.get(id=1)
        request_store = RequestStore()

        # test model blank and null fields validation
        with self.assertRaises(ValidationError) as err:
            request_store.full_clean()
        err_dict = err.exception.message_dict
        self.assertEquals(err_dict['path'][0],
                          RequestStore._meta.get_field('path').
                          error_messages['blank'])
        self.assertEquals(err_dict['method'][0],
                          RequestStore._meta.get_field('method').
                          error_messages['blank'])

        # test cretae and save object
        request_store.path = '/'
        request_store.method = 'GET'
        request_store.user = user

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
        self.assertEquals(only_request.new_request, 1)
        self.assertEquals(only_request.user, user)


class NoteModelTestCase(TestCase):
    def test_processor(self):
        " Test processor."
        note = NoteModel.objects.get(model='Person')
        self.assertEqual(note.action_type, 0)
