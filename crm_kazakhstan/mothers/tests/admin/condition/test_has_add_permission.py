from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import get_perms

from mothers.models import Mother, Condition
from mothers.admin import ConditionAdmin

User = get_user_model()
Mother: models
Condition: models


class HasViePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        self.primary_stage_group, created = Group.objects.get_or_create(name='primary_stage')

    def test_super_user_has_view_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_view_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_add_perm_obj(self):
        self.staff_user.groups.add(self.primary_stage_group)
        request = self.factory.get('/')
        request.user = self.staff_user

        view = self.admin.has_add_permission(request)
        self.assertTrue(view)
