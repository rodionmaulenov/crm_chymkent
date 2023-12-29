from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Condition
from mothers.inlines import ConditionInline

User = get_user_model()

Mother: models
Condition: models


class CleanMethodConditionInlineFormWithoutFinishedTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.mother = Mother.objects.create(name='Test Mother', number='123', program='Test Program')

    def test_condition_inline_form_when_clean_method_work_with_error_message(self):
        request = self.factory.post('/', {
            'condition_set-TOTAL_FORMS': '1',
            'condition_set-INITIAL_FORMS': '0',
            'condition_set-MIN_NUM_FORMS': '0',
            'condition_set-MAX_NUM_FORMS': '1000',
            'condition_set-0-mother': self.mother.pk,
            'condition_set-0-condition': 'WWW',
            'condition_set-0-scheduled_time': '10:00',
            'condition_set-0-scheduled_date': '',  # Deliberately left blank to test validation
        })
        request.user = self.user

        # Create the formset instance
        inline = ConditionInline(Mother, self.site)
        Formset = inline.get_formset(request, self.mother)
        formset_instance = Formset(request.POST, instance=self.mother)

        # Assert the formset is not valid due to the custom validation
        self.assertFalse(formset_instance.is_valid())

        self.assertIn('Date must be provided if time is set.', formset_instance.errors[0]['scheduled_date'])

    def test_condition_inline_form_when_clean_method_work_without_error_message(self):
        request = self.factory.post('/', {
            'condition_set-TOTAL_FORMS': '1',
            'condition_set-INITIAL_FORMS': '0',
            'condition_set-MIN_NUM_FORMS': '0',
            'condition_set-MAX_NUM_FORMS': '1000',
            'condition_set-0-mother': self.mother.pk,
            'condition_set-0-condition': 'WWW',
            'condition_set-0-scheduled_time': '10:00',
            'condition_set-0-scheduled_date': '2022-12-10',  # Deliberately left blank to test validation
        })
        request.user = self.user

        # Create the formset instance
        inline = ConditionInline(Mother, self.site)
        Formset = inline.get_formset(request, self.mother)
        formset_instance = Formset(request.POST, instance=self.mother)

        # Assert the formset is not valid due to the custom validation
        self.assertTrue(formset_instance.is_valid())

        with self.assertRaises(KeyError):
            self.assertNotIn('Date must be provided if time is set.', formset_instance.errors[0]['scheduled_date'])


class InitMethodConditionInlineFormWithoutFinished(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_when_finished_equal_True_change_not_allowed(self):
        mother_instance = Mother.objects.create(name="Test")
        Condition.objects.create(mother=mother_instance, condition='WWW', reason=None,
                                 scheduled_date=None, finished=True)

        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, admin.site)
        formset_class = inline.get_formset(request, mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=mother_instance)

        # Use _construct_form to create a form
        form = formset._construct_form(0)

        for field_name, instance in form.fields.items():
            if field_name not in ['id', 'DELETE', 'mother']:
                self.assertTrue(form.fields[field_name].disabled)


    def test_when_finished_equal_True_change_allowed(self):
        mother_instance = Mother.objects.create(name="Test")
        Condition.objects.create(mother=mother_instance, condition='WWW', reason=None,
                                 scheduled_date=None, finished=False)

        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, admin.site)
        formset_class = inline.get_formset(request, mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=mother_instance)

        # Use _construct_form to create a form
        form = formset._construct_form(0)

        for field_name, instance in form.fields.items():
            if field_name not in ['id', 'DELETE', 'mother']:
                self.assertFalse(form.fields[field_name].disabled)
