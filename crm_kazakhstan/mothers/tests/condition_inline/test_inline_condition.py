import pytz
from datetime import datetime

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Condition
from mothers.admin import MotherAdmin
from mothers.inlines import ConditionInline

User = get_user_model()

Mother: models
Condition: models


class ConditionInlineFormSetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password', timezone='Europe/Kiev')
        self.mother_instance = Mother.objects.create(name='Test Mother')

        # Set a specific UTC time for the Condition instance
        self.utc_time = datetime(2023, 12, 20, 10, 15, 12, tzinfo=pytz.UTC)
        self.condition_instance = Condition.objects.create(
            mother=self.mother_instance,
            scheduled_time=self.utc_time.time(),
            scheduled_date=self.utc_time.date()
        )

    def test_prepopulated_form_date_equal_user_local_time_and_date(self):
        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, self.site)
        formset_class = inline.get_formset(request, self.mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=self.mother_instance)

        # Check the initial data for the first form in the formset
        form = formset.forms[0]
        initial_time = form.initial.get('scheduled_time')
        initial_date = form.initial.get('scheduled_date')

        # Convert UTC time to user's local timezone and check if it matches the initial data
        user_timezone = pytz.timezone(self.user.timezone)
        expected_local_time = self.utc_time.astimezone(user_timezone)

        self.assertEqual(initial_time, expected_local_time.time())

        self.assertEqual(initial_date, expected_local_time.date())

    def test_prepopulated_form_date_equal_None(self):
        self.mother_instance = Mother.objects.create(name='Test2 Mother')

        self.condition_instance = Condition.objects.create(
            mother=self.mother_instance,
        )
        request = self.factory.get('/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, self.site)
        formset_class = inline.get_formset(request, self.mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=self.mother_instance)

        # Check the initial data for the first form in the formset
        form = formset.forms[0]
        initial_time = form.initial.get('scheduled_time')
        initial_date = form.initial.get('scheduled_date')

        # Convert UTC time to user's local timezone and check if it matches the initial data
        user_timezone = pytz.timezone(self.user.timezone)
        expected_local_time = self.utc_time.astimezone(user_timezone)

        self.assertEqual(initial_time, None)

        self.assertEqual(initial_date, None)


class ConditionInlineFormTest(TestCase):
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



