from guardian.shortcuts import assign_perm

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Permission
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from gmail_messages.models import CustomUser
from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='Mother 1')

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=CustomUser.StageChoices.PRIMARY)

    def test_superuser_has_access_for_site_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_to_site_layer_with_obj_lvl_permission(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)
        assign_perm('primary_stage', self.staff_user, self.mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_to_site_layer_with_model_lvl_perm(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_not_access_to_site_layer(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)
