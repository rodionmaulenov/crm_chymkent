from datetime import time, date
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models

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
        Stage.objects.create(mother=self.mother)
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_only_one_condition_instance(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}"><strong>recently created</strong></a>',
            result
        )

    def test_condition_and_plan(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED)
        Planned.objects.create(mother=self.mother, finished=True)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}"><strong>recently created</strong></a>', result)

    def test_condition_and_ban(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED)
        Ban.objects.create(mother=self.mother, banned=True)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/state/add/?mother={self.mother.pk}"><strong>recently created</strong></a>', result)

    def test_plan_instance_exists(self):
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED)
        Planned.objects.create(mother=self.mother, finished=False)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)
        self.assertEqual('<strong>recently created</strong>', result)

    def test_ban_instance_exists(self):
        Ban.objects.create(mother=self.mother, comment='Some Reason', banned=False)
        State.objects.create(mother=self.mother, finished=True, condition=State.ConditionChoices.CREATED)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)
        self.assertEqual('<strong>recently created</strong>', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_change_on_change_list_page_when_not_on_filtered_page(self):
        State.objects.create(mother=self.mother, finished=True,
                             condition=State.ConditionChoices.CREATED)
        condition = State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 15),
                                         scheduled_time=time(21, 20, 0),
                                         condition=State.ConditionChoices.NO_BABY)

        request = self.factory.get('/admin/mothers/mother/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        params = extract_from_url(request, 'planned_time', 'datetime')
        self.assertFalse(params)

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertEqual(
            f'<a href="/admin/mothers/state/{condition.pk}/change/"><strong>has not baby</strong></a>', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_not_change_on_change_list_page_when_not_on_filtered_page(self):
        State.objects.create(mother=self.mother, finished=True,
                             condition=State.ConditionChoices.CREATED)
        State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                             scheduled_time=time(21, 20, 0), condition=State.ConditionChoices.EMPTY,
                             reason='some reason')

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        params = extract_from_url(request, 'planned_time', 'datetime')
        self.assertFalse(params)

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertEqual('<strong>some reason</strong>', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_change_on_filtered_changelist_page(self):
        State.objects.create(mother=self.mother, finished=True,
                             condition=State.ConditionChoices.CREATED)
        condition = State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                         scheduled_time=time(21, 20, 0), reason='some reason')

        request = self.factory.get('/admin/mothers/mother/?filter_set=scheduled_event')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        params = extract_from_url(request, 'filter_set', 'scheduled_event')
        self.assertTrue(params)

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'<a href="/admin/mothers/state/{condition.pk}/change/"><strong>some reason</strong></a>', result)
