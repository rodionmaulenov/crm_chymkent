from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import BanAdmin
from mothers.models import Mother, Ban

Mother: models
Ban: models


class GetFieldsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = BanAdmin(Ban, admin.site)

    def test_change_case(self):
        mother = Mother.objects.create(name='Test Mother')
        obj = Ban.objects.create(mother=mother, comment='comment')

        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj)

        expected_fields = ()

        self.assertEqual(fields, expected_fields)

    def test_add_case(self):
        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj=None)

        expected_fields = ('mother', 'comment')

        self.assertEqual(fields, expected_fields)
