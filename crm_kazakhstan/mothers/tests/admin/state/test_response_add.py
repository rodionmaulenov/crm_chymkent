from urllib.parse import urlencode

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from mothers.models import State, Mother
from mothers.admin import StateAdmin

State: models
Mother: models

User = get_user_model()


class ResponseAddTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.condition_admin = StateAdmin(State, AdminSite())
        self.superuser = User.objects.create_superuser(username='user', password='user')

    def test_response_add_with_extra_params(self):
        mother = Mother.objects.create(name='Mother')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         condition=State.ConditionChoices.WORKING,
                                         scheduled_time=timezone.now().time())

        request = self.factory.post(
            f'/admin/mothers/condition/add/?filter_set=assign_new_state&mother={mother.pk}'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_add(request, condition)

        self.assertEqual(response.status_code, 302)
        required = reverse('admin:mothers_mother_changelist') + '?' + urlencode({'filter_set': 'assign_new_state'})
        self.assertEqual(response.url, required)

        messages = list(get_messages(request))
        expected_message = (f'We are working, successfully added for <a href="/admin/mothers/mother/{mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))

    def test_response_add(self):
        mother = Mother.objects.create(name='Mother')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         reason='test reason',
                                         scheduled_time=timezone.now().time())

        request = self.factory.post(f'/admin/mothers/condition/add/?mother={mother.pk}')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_add(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

        messages = list(get_messages(request))
        expected_message = (f'Test reason, successfully added for <a href="/admin/mothers/mother/{mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))
