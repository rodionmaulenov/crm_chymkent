from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_super_user_has_perm_if_obj(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, self.mother)

        self.assertTrue(view)

    def test_super_user_has_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request)

        self.assertTrue(view)

    def test_staff_has_perm_if_obj(self):
        assign_perm('primary_stage', self.staff_user, self.mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, self.mother)

        self.assertTrue(view)

    def test_staff_has_perm_list_layer(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)
        assign_perm('primary_stage', self.staff_user, self.mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertTrue(view)

    def test_staff_assign_model_perm_if_obj(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, self.mother)

        self.assertTrue(view)

    def test_staff_assign_model_perm_list_layer(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_any_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)
