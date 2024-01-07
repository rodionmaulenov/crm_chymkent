from datetime import datetime, time

from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from mothers.constants import CONDITION_CHOICES
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
        condition_instance = Condition.objects.create(
            mother=mother_instance,
            condition='WWW',  # Use a value that exists in CONDITION_CHOICES
            reason=None,
            scheduled_date=None,
            scheduled_time=None,
            finished=True  # Set finished to True for testing
        )

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
            if not form.initial.get(field_name) and field_name not in ['finished', 'DELETE'] and \
                    field_name not in ['scheduled_date', 'scheduled_time', 'condition']:
                self.assertIsInstance(field.widget, EmptyOnlyFieldWrapper)

        # Check the rendering for 'scheduled_date' and 'scheduled_time' when finished=True
        for field_name in ['scheduled_date', 'scheduled_time']:
            self.assertIn('empty', form.fields[field_name].widget.render(field_name, None))

        # Check the rendering for 'condition'
        condition_field = form.fields['condition'].widget.render('condition', condition_instance.condition)
        long_description = dict(CONDITION_CHOICES).get(condition_instance.condition)
        self.assertIn(long_description, condition_field)

    def test_construct_form_when_empty_scheduled_time_fields(self):
        mother_instance = Mother.objects.create(name="Test")
        condition_instance = Condition.objects.create(
            mother=mother_instance,
            condition='WWW',  # Use a value that exists in CONDITION_CHOICES
            reason=None,
            scheduled_date=datetime(2023, 12, 10, tzinfo=timezone.utc).date(),
            scheduled_time=None,
            finished=True  # Set finished to True for testing
        )

        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, admin.site)
        formset_class = inline.get_formset(request, mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=mother_instance)

        # Use _construct_form to create a form
        form = formset._construct_form(0)

        # Check the rendering for 'scheduled_date' and 'scheduled_time' when finished=True
        for field_name in ['scheduled_date', 'scheduled_time']:
            if field_name == 'scheduled_date':
                self.assertIn('empty', form.fields[field_name].widget.render(field_name, None))
            else:
                self.assertIn('2023-12-10',
                              form.fields[field_name].widget.render(field_name, condition_instance.scheduled_date))

    def test_construct_form_not_empty_fields(self):
        mother_instance = Mother.objects.create(name="Test1")
        Condition.objects.create(mother=mother_instance, condition='WWW', reason='Test',
                                 scheduled_date=datetime(2023, 12, 10, tzinfo=timezone.utc),
                                 scheduled_time=time(14, 30, 0), finished=True)
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
                self.assertNotIsInstance(field.widget.__class__, EmptyOnlyFieldWrapper)
