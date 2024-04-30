from datetime import time, date

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Mother, State, Planned, Stage
from mothers.admin import MotherAdmin


Mother: models
State: models
Planned: models
Stage: models

User = get_user_model()


class CreateStateTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_state(self):
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
        required = f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}" ><b>add new</b></a>'
        self.assertEqual(result, required)

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
        required = f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}" ><b>add new</b></a>'
        self.assertEqual(result, required)

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
        required = f'<a href="/admin/mothers/state/{state.pk}/change/" ><b>Recently created</b></a>'
        self.assertEqual(result, required)

    def test_instance_not_finished_and_not_another_adn_reason(self):
        state = State.objects.create(mother=self.mother, finished=False,
                                     scheduled_date=timezone.now().date(),
                                     scheduled_time=timezone.now().time(),
                                     reason='some reason'
                                     )

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_state(mother=self.mother)
        required = f'<a href="/admin/mothers/state/{state.pk}/change/" ><b>Some reason</b></a>'
        self.assertEqual(result, required)


