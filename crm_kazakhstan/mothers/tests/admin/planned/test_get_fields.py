from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import PlannedAdmin
from mothers.models import Planned, Mother

Mother: models
Planned: models


class GetFieldsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = PlannedAdmin(Planned, admin.site)
        self.mother = Mother.objects.create(name='Test Mother')

    def test_change_case(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('/')
        fields = self.admin.get_fields(request, planned)

        expected_fields = ('mother', 'plan', 'note', 'scheduled_date', 'scheduled_time', "created", 'finished')

        self.assertEqual(fields, expected_fields)

    def test_add_case(self):
        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj=None)

        expected_fields = ('mother', 'plan', 'note', 'scheduled_date', 'scheduled_time')

        self.assertEqual(fields, expected_fields)
