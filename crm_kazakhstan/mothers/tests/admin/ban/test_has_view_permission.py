from guardian.shortcuts import assign_perm

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from mothers.admin import BanAdmin
from mothers.models import Mother, Ban, Stage

User = get_user_model()
Mother: models
Ban: models
Stage: models


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.admin = BanAdmin(Ban, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_super_user_has_view_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, obj=None)

        self.assertTrue(view)

    def test_super_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        ban = Ban.objects.create(mother=mother, comment='some comment')
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, ban)

        self.assertTrue(view)

    def test_staff_user_has_model_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        ban = Ban.objects.create(mother=mother, comment='some comment')
        view_permission = Permission.objects.get(codename='view_ban')
        self.staff_user.user_permissions.add(view_permission)
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, ban)

        self.assertTrue(view)

    def test_staff_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        ban = Ban.objects.create(mother=mother, comment='some comment')
        assign_perm('view_ban', self.staff_user, ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, ban)

        self.assertTrue(view)

    def test_staff_user_not_has_model_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        ban = Ban.objects.create(mother=mother, comment='some comment')
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, ban)

        self.assertFalse(view)

    def test_staff_user_has_list_view_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        Ban.objects.create(mother=mother, comment='some comment')
        view_permission = Permission.objects.get(codename='view_ban')
        self.staff_user.user_permissions.add(view_permission)
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, obj=None)

        self.assertTrue(view)

    def test_staff_user_has_list_view_perm_2(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN)
        Ban.objects.create(mother=mother, comment='some comment')
        assign_perm('view_mother', self.staff_user, mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request, obj=None)

        self.assertTrue(view)