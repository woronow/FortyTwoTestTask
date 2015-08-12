# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import resolve

from datetime import date

from .models import Person
from .views import home_page


class PersonModelTests(TestCase):
    def test_creating_a_new_person_and_saving_it_to_the_database(self):
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
        self.assertEquals(len(all_persons), 1)
        only_person = all_persons[0]
        self.assertEquals(only_person, obj)

        # and check that it's saved its two attributes: name and date_of_birth
        self.assertEquals(only_person.name, 'Aleks')
        self.assertEquals(only_person.surname, 'Woronow')


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>Site Name</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>')) 