from datetime import time, date
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Mother, State, Planned, Ban, Stage
from mothers.admin import MotherAdmin
from mothers.services.mother import extract_from_url

Mother: models
State: models
Planned: models
Ban: models
Stage: models

User = get_user_model()


class CreateConditionLinkTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_state_finished_and_not_another_inst(self):
        State.objects.create(mother=self.mother, finished=True,
                             condition=State.ConditionChoices.CREATED,
                             scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)

        self.assertEqual(f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}"><b>adding</b></a>', result)

    def test_ban_exists(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED,
                             scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        Ban.objects.create(mother=self.mother, banned=False)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)

        self.assertIsNone(result)

    def test_plan_exists(self):
        State.objects.create(mother=self.mother,
                             finished=True,
                             condition=State.ConditionChoices.CREATED,
                             scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        Planned.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 15),
                               scheduled_time=time(21, 20, 0))

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)
        self.assertIsNone(result)

    def test_state_and_plan_already_finished(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED,
                             scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        Planned.objects.create(mother=self.mother, finished=True, scheduled_date=date(2023, 12, 15),
                               scheduled_time=time(21, 20, 0))

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}"><b>adding</b></a>',
            result)

    def test_instance_not_finished_and_not_another(self):
        state = State.objects.create(mother=self.mother, finished=False, condition=State.ConditionChoices.CREATED,
                                     scheduled_date=timezone.now().date(),
                                     scheduled_time=timezone.now().time()
                                     )

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)
        self.assertEqual(
            f'<a href="/admin/mothers/state/{state.pk}/change/"><strong>recently created</strong></a>',
            result)

