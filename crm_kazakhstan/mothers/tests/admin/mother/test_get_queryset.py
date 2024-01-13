from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class GetQuerySetMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        # Create a group
        self.primary_stage_group, created = Group.objects.get_or_create(name='primary_stage')

    def test_has_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertEqual(len(queryset), 2)

    def test_has_queryset_for_superuser_mothers_instance_on_another_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        self.assertEqual(len(queryset), 0)

    def test_has_queryset_for_superuser_mother_instance_on_another_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        self.assertEqual(len(queryset), 1)

    def test_empty_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)

    def test_has_queryset_for_staff_without_group_perms_and_mothers_without_obj_lvl_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertEqual(len(queryset), 0)

    def test_has_queryset_for_staff_has_group_primary_stage_and_mothers_without_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertEqual(len(queryset), 0)

    def test_queryset_for_staff_has_group_primary_stage_and_mothers_without_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertEqual(len(queryset), 0)

    def test_queryset_for_staff_has_group_primary_stage_and_mothers_with_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        self.assertEqual(len(queryset), 2)

    def test_queryset_for_staff_has_group_primary_stage_and_mother_with_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        self.assertEqual(len(queryset), 1)

    def test_queryset_for_staff_has_group_first_visit_stages_and_mother_with_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        self.assertEqual(len(queryset), 0)

    def test_queryset_for_staff_has_group_first_visit_stage_and_mother_with_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        self.assertEqual(len(queryset), 1)
