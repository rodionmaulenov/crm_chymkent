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


class HasAddPermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StateAdmin(State, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_super_user_has_add_perm_list_lvl(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_add_perm_list_lvl(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)

    def test_staff_has_add_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        State.objects.create(mother=mother)

        assign_perm('change_mother', self.staff_user, mother)
        assign_perm('view_mother', self.staff_user, mother)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_staff_has_add_obj_perm_with_model_add_lvl_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother)

        view_permission = Permission.objects.get(codename='add_state')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_add_permission(request, condition))

    def test_staff_has_not_add_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        State.objects.create(mother=mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)