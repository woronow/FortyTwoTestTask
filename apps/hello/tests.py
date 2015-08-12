# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from datetime import date

from .models import Person
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
