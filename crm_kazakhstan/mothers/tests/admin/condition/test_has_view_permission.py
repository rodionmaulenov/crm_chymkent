from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

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

    def test_super_user_has_view_perm_list_lvl(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_super_user_has_view_perm_obj_lvl(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, condition)

        self.assertTrue(view)

    def test_staff_user_has_not_view_perm_list_lvl(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_staff_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        assign_perm('view_condition', self.staff_user, condition)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_view_permission(request, condition))

    def test_staff_has_view_obj_perm_with_model_view_lvl_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        view_permission = Permission.objects.get(codename='view_condition')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_view_permission(request, condition))

    def test_staff_has_not_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, condition)

        self.assertFalse(view)
