from datetime import time, date

from django.test import TestCase, RequestFactory
from django.db import models

from mothers.forms import StateAdminForm
from mothers.models import Mother, State

Mother: models


class CleanMethodTest(TestCase):
    def setUp(self):
        self.form = StateAdminForm
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

        form = StateAdminForm(request=request, data=valid_data)

        self.assertTrue(form.is_valid())

        self.assertEqual(form.clean(), valid_data)

    def test_clean_valid_data_condition_has_not_date(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': 'no baby',
            'reason': '',
            'scheduled_date': None,
            'scheduled_time': None,
            'finished': False
        }

        form = StateAdminForm(request=request, data=valid_data)

        self.assertFalse(form.is_valid())

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

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Date must be provided if time is set.', form.errors['scheduled_date'])

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

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Time must be provided if date is set.', form.errors['scheduled_time'])

    def test_clean_condition_is_empty_and_reason_emtpy_too(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': '',
            'reason': '',
            'scheduled_date': date(12, 11, 13),
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Specify understandable reason for empty state', form.errors['reason'])

    def test_reason_without_date_and_reason(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': None,
            'reason': '',
            'scheduled_date': '',
            'scheduled_time': time(12, 0),
            'finished': False
        }

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Date must be provided if time is set.', form.errors['scheduled_date'])

    def test_reason_without_time(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': None,
            'reason': 'Test data',
            'scheduled_date': date(12, 11, 13),
            'scheduled_time': '',
            'finished': False
        }

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Time must be provided if date is set.', form.errors['scheduled_time'])

    def test_reason_without_datetime(self):
        request = self.factory.get('/')
        valid_data = {
            'mother': self.mother,
            'condition': None,
            'reason': 'Test data',
            'scheduled_date': '',
            'scheduled_time': '',
            'finished': False
        }

        form = StateAdminForm(data=valid_data, request=request)

        self.assertFalse(form.is_valid())

        self.assertIn('Specify date', form.errors['scheduled_date'])
        self.assertIn('Specify time', form.errors['scheduled_time'])
