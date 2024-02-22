from datetime import datetime, time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Condition, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import EmptyConditionFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Stage: models

User = get_user_model()


class EmptyConditionFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.factory = RequestFactory()

        self.custom_filter = EmptyConditionFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_mother_related_condition_has_empty_condition(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            reason='Some reason',
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'empty_state': 'empty_condition'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_mother_related_condition_has_empty_condition_and_already_finished(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            reason='Some reason',
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'empty_state': 'empty_condition'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    def test_several_mothers_with_empty_conditions(self):
        mother = Mother.objects.create(name='Test Mother')
        mother1 = Mother.objects.create(name='Test1 Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother1, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )
        Condition.objects.create(
            mother=mother1,
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'empty_state': 'empty_condition'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 2)

    def test_exists_2_condition_first_empty_second_created(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'empty_state': 'empty_condition'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)
