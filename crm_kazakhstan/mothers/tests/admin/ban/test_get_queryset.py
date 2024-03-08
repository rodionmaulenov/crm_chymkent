from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Stage, Ban
from mothers.admin import BanAdmin

User = get_user_model()
Stage: models
Mother: models
Ban: models


class GetQuerySetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment')

        self.assertEqual(len(queryset), 1)

    def test_queryset_for_staff_user(self):
        view_permission = Permission.objects.get(codename='view_ban')
        self.staff_user.user_permissions.add(view_permission)
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment')

        self.assertEqual(len(queryset), 1)

    def test_not_queryset_for_staff_user(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment')
        Ban.objects.create(mother=mother, comment='some comment1')

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)


