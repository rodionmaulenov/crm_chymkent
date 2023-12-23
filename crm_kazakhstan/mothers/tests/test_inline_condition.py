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

Mother:models
Condition:models


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
            scheduled_time=self.utc_time.time()
        )

    def test_condition_inline_formset_initial_data(self):
        # Create a request object for the admin change view
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user

        # Get the inline formset class
        inline = ConditionInline(Mother, self.site)
        formset_class = inline.get_formset(request, self.mother_instance)

        # Create a formset instance for the existing mother instance
        formset = formset_class(instance=self.mother_instance)

        # Check the initial data for the first form in the formset
        form = formset.forms[0]
        initial_time = form.initial.get('scheduled_time')

        # Convert UTC time to user's local timezone and check if it matches the initial data
        user_timezone = pytz.timezone(self.user.timezone)
        expected_local_time = self.utc_time.astimezone(user_timezone).time()
        self.assertEqual(initial_time, expected_local_time,
                         "The initial time in the form does not match the expected local time.")


class ConditionInlineFormTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.mother = Mother.objects.create(name='Test Mother', number='123', program='Test Program')

    def test_condition_inline_form_clean(self):
        request = self.factory.post('/', {
            'condition-TOTAL_FORMS': '1',
            'condition-INITIAL_FORMS': '0',
            'condition-MIN_NUM_FORMS': '0',
            'condition-MAX_NUM_FORMS': '1000',
            'condition-0-mother': self.mother.pk,
            'condition-0-condition': 'we talk',
            'condition-0-scheduled_time': '10:00',
            'condition-0-scheduled_date': '',  # Deliberately left blank to test validation
        })
        request.user = self.user

        # Create the formset instance
        inline = ConditionInline(Mother, self.site)
        Formset = inline.get_formset(request, self.mother)
        Formset = Formset(request.POST, instance=self.mother)

        # Assert the formset is not valid due to the custom validation
        self.assertFalse(Formset.is_valid())
        self.assertIn('Date must be provided if time is set.', Formset.errors[0]['scheduled_date'])
