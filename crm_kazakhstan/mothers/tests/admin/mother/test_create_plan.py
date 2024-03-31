from datetime import time, date

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Mother, State, Planned, Ban, Stage
from mothers.admin import MotherAdmin

Mother: models
State: models
Planned: models
Ban: models
Stage: models

User = get_user_model()


class CreatePlanTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_state_exists(self):
        State.objects.create(mother=self.mother, finished=False, condition=State.ConditionChoices.CREATED,
                             scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time()
                             )

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_plan(mother=self.mother)

        self.assertIsNone(result)

    def test_ban_instance_exists(self):
        Ban.objects.create(mother=self.mother, comment='some reason', banned=False)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_plan(mother=self.mother)
        self.assertIsNone(result)

    def test_no_instances_exist(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_plan(mother=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/planned/add/?mother={self.mother.pk}"><b>adding</b></a>', result)

    def test_plann_exists(self):
        plan = Planned.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 15),
                                      scheduled_time=time(21, 20, 0), plan=Planned.PlannedChoices.FIRST_TEST)
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_plan(mother=self.mother)
        self.assertEqual(
            f'<a href="/admin/mothers/planned/{plan.pk}/change/"><strong>laboratory is planned</strong></a>', result)
