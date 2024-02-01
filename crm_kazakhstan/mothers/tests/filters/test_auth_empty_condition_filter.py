from datetime import datetime, time
from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Condition, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import AuthEmptyConditionFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Stage: models
User = get_user_model()


class AuthEmptyConditionFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

        self.factory = RequestFactory()

        self.custom_filter = AuthEmptyConditionFilter

        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_superuser_get_access_to_filtered_queryset(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'what_reason': 'empty_condition'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    def test_staff_get_access_on_filtered_queryset_assign_on_obj_user_view_change_perm(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.__empty__,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            finished=False
        )
        assign_perm('view_mother', self.staff_user, mother)
        assign_perm('change_mother', self.staff_user, mother)

        request = self.factory.get('/')
        request.user = self.staff_user

        filter_instance = self.custom_filter(
            request, {'what_reason': 'empty_condition'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    def test_staff_get_access_on_filtered_queryset_not_assign_on_obj_user_view_change_perm(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.__empty__,
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.staff_user

        filter_instance = self.custom_filter(
            request, {'what_reason': 'empty_condition'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)

    def test_assign_model_perm_on_staff_has_filtered_queryset(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.__empty__,
            finished=False
        )
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        filter_instance = self.custom_filter(
            request, {'what_reason': 'empty_condition'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    def test_not_assign_model_perm_on_staff_has_filtered_queryset(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.__empty__,
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.staff_user

        filter_instance = self.custom_filter(
            request, {'what_reason': 'empty_condition'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)
