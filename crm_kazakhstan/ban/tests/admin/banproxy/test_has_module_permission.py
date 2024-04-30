from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AnonymousUser

from ban.admin import BanProxyAdmin
from ban.models import BanProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage

from ban.models import Ban

User = get_user_model()

Mother: models
Ban: models
Stage: models


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.admin = BanProxyAdmin(BanProxy, admin.site)
        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.BAN, finished=False)
        self.ban = Ban.objects.create(mother=self.mother, comment='some reason', banned=True)

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password',
                                                       stage=Stage.StageChoices.PRIMARY)
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)
        self.staff_user2 = User.objects.create(username='staff_user2', password='password', is_staff=True,
                                               stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_module_permission(request)

        self.assertTrue(view)

    def test_staff_has_custom_perm(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother, user=self.staff_user)

        request = self.factory.get('/')
        request.user = self.staff_user

        view = self.admin.has_module_permission(request)

        self.assertTrue(view)

        request = self.factory.get('/')
        request.user = self.staff_user2

        view = self.admin.has_module_permission(request)

        self.assertFalse(view)

    def test_staff_assign_base_perm(self):
        view_permission = Permission.objects.get(codename='view_banproxy')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_module_permission(request)

        self.assertTrue(view)

        request = self.factory.get('/')
        request.user = self.staff_user2
        view = self.admin.has_module_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_not_any_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_module_permission(request)

        self.assertFalse(view)

    def test_anonymous_user_has_not_any_perms(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = self.admin.has_module_permission(request)

        self.assertFalse(view)
