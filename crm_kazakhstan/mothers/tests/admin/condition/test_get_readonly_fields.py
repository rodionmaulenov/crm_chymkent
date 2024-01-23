from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite

from mothers.admin import ConditionAdmin
from mothers.models import Condition, Mother

Mother: models
Condition: models


class GetReadOnlyFieldsMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ConditionAdmin(Condition, AdminSite())

    def test_get_readonly_fields_on_add(self):
        request = self.factory.get('/admin/yourapp/yourmodel/add/')
        readonly_fields = self.admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, ())

    def test_get_readonly_fields_on_change(self):
        mother = Mother.objects.create(name='Test Mother')
        obj = Condition.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/admin/yourapp/yourmodel/{}/change/'.format(obj.pk))
        readonly_fields = self.admin.get_readonly_fields(request, obj)
        self.assertEqual(readonly_fields, self.admin.readonly_fields)
