from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import StateAdmin
from mothers.models import State, Mother

Mother: models
State: models


class GetFieldsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = StateAdmin(State, admin.site)

    def test_change_case(self):
        mother = Mother.objects.create(name='Test Mother')
        obj = State.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition=State.ConditionChoices.NO_BABY,
            finished=False
        )

        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj)

        expected_fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished')

        self.assertEqual(fields, expected_fields)

    def test_add_case(self):
        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj=None)

        expected_fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time')

        self.assertEqual(fields, expected_fields)
