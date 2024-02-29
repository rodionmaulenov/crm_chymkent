from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models

from mothers.models import Mother, State, Planned, Ban
from mothers.admin import MotherAdmin

Mother: models
State: models
Planned: models
Ban: models

User = get_user_model()


class CreateBanTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_plan_exists(self):
        Planned.objects.create(mother=self.mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=False)
        Ban.objects.create(mother=self.mother, comment='some comment', banned=True)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result, '-')

    def test_plan_exists_and_ban(self):
        Planned.objects.create(mother=self.mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=False)
        Ban.objects.create(mother=self.mother, comment='some comment', banned=False)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result, None)

    def test_state_exists(self):
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.CREATED, finished=True)
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.NO_BABY, finished=False)
        Ban.objects.create(mother=self.mother, comment='some comment', banned=True)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result, '-')

    def test_state_exists_and_ban(self):
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.CREATED, finished=True)
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.NO_BABY, finished=False)
        Ban.objects.create(mother=self.mother, comment='some comment', banned=False)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result, None)

    def test_add_ban(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result,
                         f'<a href="/admin/mothers/ban/add/?mother={self.mother.pk}"><strong>to ban</strong></a>')

    def test_add_ban_2(self):
        Planned.objects.create(mother=self.mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=True)
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.CREATED, finished=True)
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(result,
                         f'<a href="/admin/mothers/ban/add/?mother={self.mother.pk}"><strong>to ban</strong></a>')

    def test_only_ban(self):
        Planned.objects.create(mother=self.mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=True)
        State.objects.create(mother=self.mother, condition=State.ConditionChoices.CREATED, finished=True)
        Ban.objects.create(mother=self.mother, comment='some comment', banned=False)
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_ban(obj=self.mother)
        self.assertEqual(
            result,
            '<img src="/static/mothers/icons/red_check_mark.jpg" alt="Failure" style="width: 18px; height: 20px;"/>'
        )
