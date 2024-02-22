from datetime import datetime, time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Condition, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import CreatedStatusFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Stage: models

User = get_user_model()


class CreatedStatusFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

        self.factory = RequestFactory()

        self.custom_filter = CreatedStatusFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_just_now_created(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'recently_created': 'status_created'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_just_now_created_several_mothers(self):
        mother = Mother.objects.create(name='Test Mother')
        mother1 = Mother.objects.create(name='Test1 Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother1, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )
        Condition.objects.create(
            mother=mother1,
            condition=Condition.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'recently_created': 'status_created'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 2)

    def test_just_now_created_with_another_condition_instances(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'recently_created': 'status_created'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)
