# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse

from datetime import date

from ..forms import PersonForm


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
        response = self.client.get(reverse('hello:form'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:form'))
        self.assertIn('name', response.content)
