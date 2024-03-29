from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Ban, Stage
from mothers.admin import BanAdmin

User = get_user_model()

Mother: models
Ban: models


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_superuser_has_access_for_site_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_to_site_layer(self):
        mother = Mother.objects.create(name='Mother 1')
        ban = Ban.objects.create(mother=mother, comment='some comment', banned=False)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        assign_perm('ban_state', self.staff_user, ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_to_site_layer_2(self):
        view_permission = Permission.objects.get(codename='view_ban')
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