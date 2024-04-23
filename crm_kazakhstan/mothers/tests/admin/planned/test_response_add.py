from datetime import date, time
from urllib.parse import urlencode

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from mothers.models import Mother, Planned
from mothers.admin import PlannedAdmin

Planned: models
Mother: models

User = get_user_model()


class ResponseAddTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.plan_admin = PlannedAdmin(Planned, admin.site)
        self.superuser = User.objects.create_superuser(username='user', password='user')
        self.mother = Mother.objects.create(name='Mother')
        self.planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

    def test_response_add_with_extra_params(self):
        request = self.factory.post(
            f'/admin/mothers/planned/add/?filter_set=assign_new_plan&mother={self.mother.pk}'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.plan_admin.response_add(request, self.planned)

        self.assertEqual(response.status_code, 302)
        required = reverse('admin:mothers_mother_changelist') + '?' + urlencode({'filter_set': 'assign_new_plan'})
        self.assertEqual(response.url, required)

        messages = list(get_messages(request))
        expected_message = (f'Laboratory plan successfully added for <a href="/admin/mothers/mother/{self.mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))

    def test_response_add(self):
        request = self.factory.post(f'/admin/mothers/planned/add/?mother={self.mother.pk}')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.plan_admin.response_add(request, self.planned)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

        messages = list(get_messages(request))
        expected_message = (f'Laboratory plan successfully added for <a href="/admin/mothers/mother/{self.mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))
