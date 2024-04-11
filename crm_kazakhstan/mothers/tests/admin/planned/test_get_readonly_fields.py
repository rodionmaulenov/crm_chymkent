from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import PlannedAdmin
from mothers.models import Planned, Mother

Mother: models
Planned: models


class GetReadOnlyFieldsMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = PlannedAdmin(Planned, admin.site)

    def test_get_readonly_fields_when_add(self):
        request = self.factory.get('/admin/mothers/mother/add/')
        readonly_fields = self.admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, ())

    def test_get_readonly_fields_when_change(self):
        mother = Mother.objects.create(name='Test Mother')
        planned = Planned.objects.create(
            mother=mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)
        request = self.factory.get('/admin/mothers/mother/{}/change/'.format(planned.pk))
        readonly_fields = self.admin.get_readonly_fields(request, planned)
        self.assertEqual(readonly_fields, ('mother', 'display_plan', 'note', 'display_date', 'display_time'))
