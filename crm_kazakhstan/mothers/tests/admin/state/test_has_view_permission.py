from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

from mothers.models import Mother, State
from mothers.admin import StateAdmin

User = get_user_model()
Mother: models
State: models


class HasViePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StateAdmin(State, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_super_user_has_perm_obj_lvl(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, condition)

        self.assertTrue(view)

    def test_super_user_has_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_staff_has_perm_if_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother)
        assign_perm('primary_state', self.staff_user, condition)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_view_permission(request, condition))

    def test_staff_has_perm_with_model_lvl_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother)
        view_permission = Permission.objects.get(codename='view_state')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_view_permission(request, condition))

    def test_staff_has_not_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, condition)

        self.assertFalse(view)

    def test_staff_user_has_not_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)