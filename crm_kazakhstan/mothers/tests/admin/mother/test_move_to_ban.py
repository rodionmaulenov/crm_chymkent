from datetime import date, time

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages import get_messages
from django.db import models
from django.urls import reverse

from gmail_messages.services.manager_factory import ManagerFactory
from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage, Planned

from ban.models import Ban

User = get_user_model()

Mother: models
Stage: models
Planned: models
Ban: models


class MoveToBanTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()
        self.session = SessionMiddleware()
        self.message = MessageMiddleware()
        self.mother = Mother.objects.create(name='Test mother')
        self.user = User.objects.create(username='username', password='password', is_staff=True,
                                        stage=Stage.StageChoices.PRIMARY)

    def prepare_request(self, request):
        self.session.process_request(request)
        self.message.process_request(request)

    def test_moved_to_ban_with_custom_perm(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=self.mother, comment='comment')

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=self.mother)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, f'/admin/ban/ban/add/?mother={self.mother.pk}')

        messages = list(get_messages(request))
        with self.assertRaises(IndexError):
            x = messages[0]

    def test_moved_to_ban_with_model_perm(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=self.mother, comment='comment')

        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, f'/admin/ban/ban/add/?mother={self.mother.pk}')

        messages = list(get_messages(request))
        with self.assertRaises(IndexError):
            x = messages[0]

    def test_when_mother_has_another_actions(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)
        Ban.objects.create(mother=self.mother, comment='comment')

        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        change_url = reverse('admin:mothers_mother_changelist')
        self.assertEqual(result.url, change_url)

        messages = list(get_messages(request))
        expected_message = '<b>Test mother</b> has no finished action'
        self.assertEqual(expected_message, str(messages[0]))

    def test_when_queryset_greater_one(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=self.mother, comment='comment')

        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=self.mother, comment='comment2')

        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 2)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        full_url = reverse('admin:mothers_mother_changelist')
        self.assertEqual(result.url, full_url)

        messages = list(get_messages(request))
        expected_message = 'Please choose exactly one instance'
        self.assertEqual(expected_message, str(messages[0]))
