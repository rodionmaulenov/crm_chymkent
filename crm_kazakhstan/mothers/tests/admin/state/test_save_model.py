from datetime import date, time

import pytz

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from urllib.parse import urlencode
from django.utils import timezone
from freezegun import freeze_time
from guardian.shortcuts import get_perms

from mothers.models import State, Mother
from mothers.admin import StateAdmin

User = get_user_model()

State: models
Mother: models


class SaveModelTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StateAdmin(State, self.site)
        self.factory = RequestFactory()

        self.staff_user_without_local_time = User.objects.create_superuser(username='admin', password='password',
                                                                           is_staff=True)
        self.super_user_with_local_time = User.objects.create_superuser(username='admin1', password='password',
                                                                        timezone='Europe/Kyiv')
        self.rushana = User.objects.create_user(username='Rushana', password='password')

    def test_add_first_condition_created(self):
        mother = Mother.objects.create(name='Mother')
        form_data = {
            'mother': mother.pk,
            'condition': 'created',
            'reason': '',
            'scheduled_date': None,
            'scheduled_time': None,
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_add')
        query_params = {'mother': mother.pk, '_changelist_filters': '/admin/mothers/mother/'}
        url = f"{relative_path}?{urlencode(query_params)}"

        request = self.factory.get(url)
        request.user = self.staff_user_without_local_time

        form_class = self.admin.get_form(request=request, change=False)

        form_instance = form_class(data=form_data, instance=None)

        with self.assertRaises(AssertionError):
            self.fail(f'Form is not valid: {form_instance.errors}')

    def test_add_second_condition_created_raise_error(self):
        mother = Mother.objects.create(name='Mother')
        State.objects.create(mother=mother, condition=State.ConditionChoices.CREATED)
        form_data = {
            'mother': mother.pk,
            'condition': 'created',
            'reason': '',
            'scheduled_date': None,
            'scheduled_time': None,
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_add')
        query_params = {'mother': mother.pk, '_changelist_filters': '/admin/mothers/mother/'}
        url = f"{relative_path}?{urlencode(query_params)}"

        request = self.factory.get(url)
        request.user = self.staff_user_without_local_time

        form_class = self.admin.get_form(request=request, change=False)

        form_instance = form_class(data=form_data, instance=None)

        if form_instance.is_valid():
            obj = form_instance.save(commit=False)
            self.admin.save_model(request=request, obj=obj, form=form_instance, change=False)

            obj.refresh_from_db()
            self.assertIsNone(obj.pk)

            self.assertEqual(obj.scheduled_date, None)
            self.assertEqual(obj.scheduled_time, None)

        else:
            with self.assertRaises(AssertionError):
                self.fail(f'Form is not valid: {form_instance.errors}')

    @freeze_time("2024-01-18 12:00:00")
    def test_add_condition_scheduled_date_and_time_without_local_user_time(self):
        mother = Mother.objects.create(name='Mother')
        State.objects.create(mother=mother, condition=State.ConditionChoices.CREATED)
        form_data = {
            'mother': mother.pk,
            'condition': 'no baby',
            'reason': '',
            'scheduled_date': date(2024, 1, 18),
            'scheduled_time': time(1, 0, 0),
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_add')
        query_params = {'mother': mother.pk, '_changelist_filters': '/admin/mothers/mother/'}
        url = f"{relative_path}?{urlencode(query_params)}"

        request = self.factory.get(url)
        request.user = self.staff_user_without_local_time

        form_class = self.admin.get_form(request=request, change=False)

        form_instance = form_class(data=form_data, instance=None)

        if form_instance.is_valid():
            obj = form_instance.save(commit=False)
            self.admin.save_model(request=request, obj=obj, form=form_instance, change=False)

            obj.refresh_from_db()
            self.assertIsNotNone(obj.pk)

            self.assertEqual(obj.scheduled_date, date(2024, 1, 18))
            self.assertEqual(obj.scheduled_time, time(1, 0, 0))

        else:
            self.fail(f'Form is not valid: {form_instance.errors}')

    @freeze_time("2024-01-18 12:00:00")
    def test_change_condition_scheduled_date_and_time_without_local_user_time(self):
        mother = Mother.objects.create(name='Mother')
        # Create an existing Condition instance
        existing_condition = State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.NO_BABY,
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(12, 0, 0)
        )

        # Kyiv is typically UTC+2 or UTC+3 depending on DST, adjust accordingly
        kyiv_timezone = pytz.timezone('Europe/Kyiv')
        timezone.activate(kyiv_timezone)

        # Data to update the condition
        form_data = {
            'mother': mother.pk,
            'condition': 'no baby',
            'reason': 'Updated reason',
            'scheduled_date': date(2024, 1, 18),
            'scheduled_time': time(14, 0, 0),
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_change', args=[existing_condition.pk])
        url = f"{relative_path}?{urlencode({'mother': mother.pk})}"

        request = self.factory.get(url)
        request.user = self.staff_user_without_local_time

        form_class = self.admin.get_form(request=request, obj=existing_condition, change=True)
        form_instance = form_class(data=form_data, instance=existing_condition)

        if form_instance.is_valid():
            self.admin.save_model(request=request, obj=existing_condition, form=form_instance, change=True)
            existing_condition.refresh_from_db()

            self.assertEqual(existing_condition.scheduled_date, date(2024, 1, 18))
            self.assertEqual(existing_condition.scheduled_time, time(14, 0, 0),)
            self.assertEqual(existing_condition.reason, 'Updated reason')
        else:
            self.fail(f'Form is not valid: {form_instance.errors}')

        timezone.deactivate()

    @freeze_time("2024-01-18 12:00:00")
    def test_change_condition_scheduled_date_and_time_with_local_user_time(self):
        mother = Mother.objects.create(name='Mother')
        # Create an existing Condition instance
        existing_condition = State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.NO_BABY,
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(12, 0, 0)
        )

        # Kyiv is typically UTC+2 or UTC+3 depending on DST, adjust accordingly
        kyiv_timezone = pytz.timezone('Europe/Kyiv')
        timezone.activate(kyiv_timezone)

        # Data to update the condition
        form_data = {
            'mother': mother.pk,
            'condition': 'no baby',
            'reason': 'Updated reason',
            'scheduled_date': date(2024, 1, 18),
            'scheduled_time': time(14, 0, 0),
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_change', args=[existing_condition.pk])
        url = f"{relative_path}?{urlencode({'mother': mother.pk})}"

        request = self.factory.get(url)
        request.user = self.super_user_with_local_time

        form_class = self.admin.get_form(request=request, obj=existing_condition, change=True)
        form_instance = form_class(data=form_data, instance=existing_condition)

        if form_instance.is_valid():
            self.admin.save_model(request=request, obj=existing_condition, form=form_instance, change=True)
            existing_condition.refresh_from_db()

            self.assertEqual(existing_condition.scheduled_date, date(2024, 1, 18))
            self.assertEqual(existing_condition.scheduled_time, time(12, 0, 0), )
            self.assertEqual(existing_condition.reason, 'Updated reason')
        else:
            self.fail(f'Form is not valid: {form_instance.errors}')

        timezone.deactivate()

    def test_aa_condition_with_perms_change_and_view(self):
        mother = Mother.objects.create(name='Mother')
        obj = State(mother=mother, scheduled_date=date(2024, 1, 18))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.rushana

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)

        perms = get_perms(self.rushana, obj)
        self.assertIn('view_state', perms)
        self.assertIn('change_state', perms)
