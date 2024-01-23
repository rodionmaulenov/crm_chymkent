from unittest.mock import patch

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import ConditionAdmin
from mothers.models import Condition, Mother

Condition: models


class FormFieldForChoiceFieldMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = ConditionAdmin(Condition, admin.site)

    def test_formfield_for_choice_field_add(self):
        request = self.factory.get('/admin/yourapp/yourmodel/add/')
        db_field = Condition._meta.get_field('condition')

        # Simulate 'add' action by ensuring current_obj is None
        self.admin.current_obj = None

        formfield = self.admin.formfield_for_choice_field(db_field, request)
        choices = formfield.choices

        self.assertNotIn(('created', 'Created'), choices)

    def test_formfield_for_choice_field_change(self):
        request = self.factory.get('/admin/yourapp/yourmodel/123/change/')
        db_field = Condition._meta.get_field('condition')

        mother = Mother.objects.create(name='Test')
        condition_instance = Condition.objects.create(mother=mother)
        self.admin.current_obj = condition_instance

        formfield = self.admin.formfield_for_choice_field(db_field, request)
        choices = formfield.choices

        self.assertNotIn(('created', 'Created'), choices)