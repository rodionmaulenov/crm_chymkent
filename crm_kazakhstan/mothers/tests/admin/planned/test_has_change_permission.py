from datetime import date, time

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Planned, Stage
from mothers.admin import PlannedAdmin

User = get_user_model()
Mother: models
Planned: models


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = PlannedAdmin(Planned, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')
        self.superuser = User.objects.create_superuser('admin', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_perm_obj_lvl(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request, planned)

        self.assertTrue(view)

    def test_super_user_has_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_has_obj_perm_with_custom_perm(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=planned)

        request = self.factory.get('/')
        request.user = self.staff_user

        result = self.admin.has_change_permission(request, planned)

        self.assertTrue(result)

    def test_staff_has_obj_perm_with_model_perm(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        view_permission = Permission.objects.get(codename='change_planned')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        result = self.admin.has_change_permission(request, planned)

        self.assertTrue(result)

    def test_staff_has_not_custom_perm(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, planned)

        self.assertFalse(view)

    def test_staff_has_not_model_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)
