from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import AuthDateFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Stage: models
User = get_user_model()


class AuthDateFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

        self.factory = RequestFactory()

        self.admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, self.admin_site)

    def test_get_access_super_user_today_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Today")
        mother.date_create = timezone.now()
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = AuthDateFilter(request=request, params={'date_filter': 'today'}, model=Mother,
                           model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Today')

    def test_get_access_staff_user_with_obj_assign_perms_today_filter(self):
        request = self.factory.get('/')
        request.user = self.staff_user

        mother = Mother.objects.create(name="Today")
        mother.date_create = timezone.now()
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.staff_user, mother)
        assign_perm('change_mother', self.staff_user, mother)

        f = AuthDateFilter(request=request, params={'date_filter': 'today'}, model=Mother,
                           model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Today')

    def test_get_access_staff_user_with_model_lvl_perms_today_filter(self):
        request = self.factory.get('/')
        request.user = self.staff_user

        mother = Mother.objects.create(name="Today")
        mother.date_create = timezone.now()
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        f = AuthDateFilter(request=request, params={'date_filter': 'today'}, model=Mother,
                           model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Today')

    def test_not_access_staff_user_today_filter(self):
        request = self.factory.get('/')
        request.user = self.staff_user

        mother = Mother.objects.create(name="Today")
        mother.date_create = timezone.now()
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = AuthDateFilter(request=request, params={'date_filter': 'today'}, model=Mother,
                           model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        with self.assertRaises(AttributeError):
            self.assertEqual(queryset.first().name, 'Today')
