from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import ConditionAdmin
from mothers.models import Condition, Mother

Mother: models
Condition: models


class GetReadOnlyFieldsMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ConditionAdmin(Condition, admin.site)

    def test_change_object_how_fields_in_form_exist(self):
        mother = Mother.objects.create(name='Test Mother')
        obj = Condition.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.NO_BABY,
            finished=False
        )

        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj)

        expected_fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished')

        self.assertEqual(fields, expected_fields)

    def test_add_object_how_fields_in_form_exist(self):
        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj=None)

        expected_fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time')

        self.assertEqual(fields, expected_fields)
