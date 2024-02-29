from datetime import date, time

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import BanAdmin
from mothers.models import Ban, Mother

Mother: models
Ban: models


class GetReadOnlyFieldsMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = BanAdmin(Ban, admin.site)

    def test_get_readonly_fields_when_add(self):
        request = self.factory.get('/')
        readonly_fields = self.admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, ())

    def test_get_readonly_fields_when_change(self):
        mother = Mother.objects.create(name='Test Mother')
        obj = Ban.objects.create(mother=mother, comment='comment')

        request = self.factory.get('/')
        readonly_fields = self.admin.get_readonly_fields(request, obj)
        self.assertEqual(readonly_fields, self.admin.readonly_fields)
