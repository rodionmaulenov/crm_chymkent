from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.utils import timezone

from mothers.admin import StateAdmin
from mothers.models import State, Mother

State: models
Mother: models


class FormFieldForChoiceFieldMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = StateAdmin(State, admin.site)

    def test_formfield_for_choice_field_add(self):
        request = self.factory.get('/admin/yourapp/yourmodel/add/')
        db_field = State._meta.get_field('condition')

        # Simulate 'add' action by ensuring current_obj is None
        self.admin.current_obj = None

        formfield = self.admin.formfield_for_choice_field(db_field, request)
        choices = formfield.choices

        self.assertNotIn(('created', 'Created'), choices)

    def test_formfield_for_choice_field_change(self):
        request = self.factory.get('/admin/yourapp/yourmodel/123/change/')
        db_field = State._meta.get_field('condition')

        mother = Mother.objects.create(name='Test')
        condition_instance = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                                  scheduled_time=timezone.now().time())
        self.admin.current_obj = condition_instance

        formfield = self.admin.formfield_for_choice_field(db_field, request)
        choices = formfield.choices

        self.assertNotIn(('created', 'Created'), choices)
