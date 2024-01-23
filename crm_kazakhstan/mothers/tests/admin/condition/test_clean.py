from datetime import time, date

from django.test import TestCase, RequestFactory
from django.db import models

from mothers.forms import ConditionAdminForm
from mothers.models import Mother

Mother: models


class CleanMethodTest(TestCase):
    def setUp(self):
        self.form = ConditionAdminForm
        self.mother = Mother.objects.create(name="test")
        self.factory = RequestFactory()

    def test_clean_valid_data(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'no baby',
            'reason': '',
            'scheduled_date': date(2022, 1, 1),
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = ConditionAdminForm(request=request, data=valid_data)

        self.assertTrue(form.is_valid())

        self.assertEqual(form.clean(), valid_data)

    def test_clean_valid_data_condition_has_not_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'created',
            'reason': '',
            'scheduled_date': None,
            'scheduled_time': None,
            'finished': False
        }

        form = ConditionAdminForm(request=request, data=valid_data)

        self.assertTrue(form.is_valid())

        self.assertEqual(form.clean(), valid_data)

    def test_clean_time_without_date_and_condition_has_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'no baby',
            'reason': '',
            'scheduled_date': '',
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = ConditionAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Date must be provided if time is set.', form.errors['scheduled_date'])
        self.assertIn('Date and Time must be provided if this state is set.', form.errors['condition'])

    def test_clean_time_without_time_and_condition_has_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'no baby',
            'reason': '',
            'scheduled_date': date(2022, 1, 1),
            'scheduled_time': '',
            'finished': False
        }

        form = ConditionAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Time must be provided if date is set.', form.errors['scheduled_time'])
        self.assertIn('Date and Time must be provided if this state is set.', form.errors['condition'])

    def test_clean_time_with_date_and_condition_has_not_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'created',
            'reason': '',
            'scheduled_date': date(2022, 1, 1),
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = ConditionAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Date and Time not be set for this state.', form.errors['condition'])

    def test_clean_time_without_date_and_condition_has_not_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'created',
            'reason': '',
            'scheduled_date': '',
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = ConditionAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Date must be provided if time is set.', form.errors['scheduled_date'])
        self.assertIn('Date and Time not be set for this state.', form.errors['condition'])

    def test_clean_time_without_time_and_condition_has_not_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'created',
            'reason': '',
            'scheduled_date': date(12, 11, 13),
            'scheduled_time': '',
            'finished': False
        }

        form = ConditionAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Time must be provided if date is set.', form.errors['scheduled_time'])
        self.assertIn('Date and Time not be set for this state.', form.errors['condition'])
