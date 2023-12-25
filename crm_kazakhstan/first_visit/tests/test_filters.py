from datetime import datetime

from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from first_visit.admin import PrimaryVisitAdmin, Stage
from first_visit.filters import AuthPlannedVisitListFilter
from first_visit.models import FirstVisit
from mothers.models import Mother, Planned

User = get_user_model()
Mother: models
Planned: models


class AuthPlannedVisitListFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(username='testuser', password='testpassword', is_staff=True,
                                                  is_superuser=True)
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

        self.factory = RequestFactory()

        self.mother_first_visit_stage = PrimaryVisitAdmin(FirstVisit, admin.site)

        self.mother = Mother.objects.create(name='Test Mother')
        mother2 = Mother.objects.create(name='Test2 Mother')
        self.mother3 = Mother.objects.create(name='Test3 Mother')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=self.mother3, stage=Stage.StageChoices.PRIMARY)

        self.plan = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.TAKE_TESTS,
            scheduled_date=datetime(2023, 12, 27, tzinfo=timezone.utc)
        )

        Planned.objects.create(
            mother=mother2,
            plan=Planned.PlannedChoices.TAKE_TESTS,
            scheduled_date=datetime(2023, 12, 28, tzinfo=timezone.utc)
        )

        Planned.objects.create(
            mother=self.mother3,
            plan=Planned.PlannedChoices.TAKE_TESTS,
            scheduled_date=datetime(2023, 12, 29, tzinfo=timezone.utc)
        )

        # data for after_tests
        mother5 = Mother.objects.create(name='Test5 Mother')
        mother6 = Mother.objects.create(name='Test6 Mother')

        Stage.objects.create(mother=mother6, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother5, stage=Stage.StageChoices.PRIMARY)

        Planned.objects.create(
            mother=mother6,
            plan=Planned.PlannedChoices.TAKE_TESTS,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc)
        )

        Planned.objects.create(
            mother=mother5,
            plan=Planned.PlannedChoices.TAKE_TESTS,
            scheduled_date=datetime(2023, 12, 9, tzinfo=timezone.utc)
        )

    @freeze_time("2023-12-12")
    def test_filter_planned_visit_on_tests(self):
        request = self.factory.get('admin/first_visit/firstvisit/')
        request.user = self.superuser

        filter_instance = AuthPlannedVisitListFilter(
            request, {"plan": "tests"}, FirstVisit, self.mother_first_visit_stage
        )
        queryset = filter_instance.queryset(request, self.mother_first_visit_stage.get_queryset(request))

        self.assertEqual(len(queryset), 3)

    @freeze_time("2023-12-12")
    def test_filter_planned_visit_on_tests_2(self):
        # Mother without planned
        mother = Mother.objects.create(name='Test4 Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        request = self.factory.get('admin/first_visit/firstvisit/')
        request.user = self.superuser

        filter_instance = AuthPlannedVisitListFilter(
            request, {"plan": "tests"}, FirstVisit, self.mother_first_visit_stage
        )
        queryset = filter_instance.queryset(request, self.mother_first_visit_stage.get_queryset(request))

        self.assertEqual(len(queryset), 3)
        self.assertEqual(len(self.mother_first_visit_stage.get_queryset(request)), 6)

    @freeze_time("2023-12-12")
    def test_staff_user_has_not_permissions_filter_planned_visit_on_tests(self):
        request = self.factory.get('admin/first_visit/firstvisit/')
        request.user = self.staff_user

        filter_instance = AuthPlannedVisitListFilter(
            request, {"plan": "tests"}, FirstVisit, self.mother_first_visit_stage
        )
        queryset = filter_instance.queryset(request, self.mother_first_visit_stage.get_queryset(request))

        self.assertIsNone(queryset)

    @freeze_time("2023-12-12")
    def test_staff_user_with_permissions_filter_planned_visit_on_tests(self):
        request = self.factory.get('admin/first_visit/firstvisit/')
        can_view_mother_permission = Permission.objects.get(
            codename='view_mother')
        manage_on_first_stage = Permission.objects.get(
            codename='to_manager_on_first_stage')
        self.staff_user.user_permissions.add(can_view_mother_permission, manage_on_first_stage)
        request.user = self.staff_user

        filter_instance = AuthPlannedVisitListFilter(
            request, {"plan": "tests"}, FirstVisit, self.mother_first_visit_stage
        )
        queryset = filter_instance.queryset(request, self.mother_first_visit_stage.get_queryset(request))

        self.assertEqual(len(queryset), 3)

    @freeze_time("2023-12-12")
    def test_filter_after_planned_visit_on_tests(self):
        request = self.factory.get('admin/first_visit/firstvisit/')
        request.user = self.superuser

        filter_instance = AuthPlannedVisitListFilter(
            request, {"plan": "after_tests"}, FirstVisit, self.mother_first_visit_stage
        )
        queryset = filter_instance.queryset(request, self.mother_first_visit_stage.get_queryset(request))

        self.assertEqual(len(queryset), 2)


