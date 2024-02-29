from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django import forms
from django.db import models

from mothers.forms import StateAdminForm
from mothers.models import Mother, State
from mothers.services.mother import convert_utc_to_local

Mother: models
State: models

User = get_user_model()


class ConditionAdminFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='Test Mother')
        self.user = User.objects.create_superuser(username='test_name', password='password')

    def test_init_new_instance(self):
        # Simulate a GET request with a mother ID
        request = self.factory.get('/admin/app/condition/add/?mother=' + str(self.mother.id))

        form = StateAdminForm(request=request)

        self.assertIsInstance(form.fields['mother'].widget, forms.HiddenInput)

        self.assertEqual(form.initial['mother'], str(self.mother.id))

    def test_change_instance_initial_values(self):
        mother = Mother.objects.create(name='Test Mother')
        condition = State.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.user

        form = StateAdminForm(instance=condition, request=request)

        local_datetime = convert_utc_to_local(
            request, condition.scheduled_date, condition.scheduled_time
        )

        self.assertEqual(form.initial['scheduled_date'], local_datetime.date())
        self.assertEqual(form.initial['scheduled_time'], local_datetime.time())
