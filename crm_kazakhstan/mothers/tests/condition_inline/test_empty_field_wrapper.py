from datetime import datetime, time

from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from mothers.models import Condition, Mother
from mothers.inlines import EmptyOnlyFieldWrapper, ConditionInline

Mother: models
Condition: models
User = get_user_model()


class CustomConditionInlineFormsetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_construct_form_empty_fields(self):
        mother_instance = Mother.objects.create(name="Test")
        Condition.objects.create(mother=mother_instance, condition='WWW', reason=None,
                                 scheduled_date=None)

        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, admin.site)
        formset_class = inline.get_formset(request, mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=mother_instance)

        # Use _construct_form to create a form
        form = formset._construct_form(0)

        # Check if the empty fields are wrapped with EmptyOnlyFieldWrapper
        for field_name, field in form.fields.items():
            if not form.initial.get(field_name) and field_name not in ['finished', 'DELETE']:
                self.assertIsInstance(field.widget, EmptyOnlyFieldWrapper)

    def test_construct_form_not_empty_fields(self):
        mother_instance = Mother.objects.create(name="Test1")
        Condition.objects.create(mother=mother_instance, condition='WWW', reason='Test',
                                 scheduled_date=datetime(2023, 12, 10, tzinfo=timezone.utc),
                                 scheduled_time=time(14, 30, 0),  finished=True)
        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, admin.site)
        formset_class = inline.get_formset(request, mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=mother_instance)

        # Use _construct_form to create a form
        form = formset._construct_form(0)

        # Check if the empty fields are wrapped with EmptyOnlyFieldWrapper
        for field_name, field in form.fields.items():
            if form.initial.get(field_name):
                self.assertNotIsInstance(field.widget, EmptyOnlyFieldWrapper)
