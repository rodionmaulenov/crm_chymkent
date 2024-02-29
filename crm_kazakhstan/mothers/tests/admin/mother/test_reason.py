from datetime import date, time

from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models

from mothers.models import Mother, State
from mothers.admin import MotherAdmin

Mother: models
State: models


class ReasonTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.mother = Mother.objects.create(name='Test')

    def test_reason_exists(self):
        State.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='some reason',
            finished=False
        )
        reason = self.mother_admin.reason(self.mother)
        self.assertEqual(reason, 'some reason')

    def test_empty_reason_exists(self):
        State.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='',
            finished=False
        )
        reason = self.mother_admin.reason(self.mother)
        self.assertEqual(reason, '')

    def test_last_reason_exists(self):
        State.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='',
            finished=True
        )
        State.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='last reason',
            finished=False
        )
        reason = self.mother_admin.reason(self.mother)
        self.assertEqual(reason, 'last reason')
