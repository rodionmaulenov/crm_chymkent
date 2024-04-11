from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from ban.admin import BanProxyAdmin
from ban.models import BanProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import MotherAdmin
from mothers.models import Mother, Ban, Stage

User = get_user_model()
Mother: models
Ban: models
Stage: models


class GetQuerysetTest(TestCase):
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

    def test_super_user(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

    def test_staff_user(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

    def test_staff_user_has_not_query(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)

    def test_staff_users_has_or_not_queryset(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother, user=self.staff_user)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

        request = self.factory.get('/')
        request.user = self.staff_user2
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)
