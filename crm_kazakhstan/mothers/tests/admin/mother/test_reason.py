from datetime import date, time

from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models

from mothers.models import Mother, Condition
from mothers.admin import MotherAdmin

Mother: models
Condition: models


class ReasonTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.mother = Mother.objects.create(name='Test')

    def test_reason_exists(self):
        Condition.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='some reason',
            finished=False
        )
        reason = self.mother_admin.reason(self.mother)
        self.assertEqual(reason, 'some reason')

    def test_empty_reason_exists(self):
        Condition.objects.create(
            mother=self.mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            reason='',
            finished=False
        )
        reason = self.mother_admin.reason(self.mother)
        self.assertEqual(reason, '')
