from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from gmail_messages.services.manager_factory import ManagerFactory
from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class GetQuerysetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_has_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.assertEqual(len(queryset), 2)

    def test_has_queryset_for_superuser_mothers_instance_on_another_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        self.assertEqual(len(queryset), 0)

    def test_has_queryset_for_superuser_mother_instance_mix_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        self.assertEqual(len(queryset), 1)

    def test_empty_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)

    def test_has_queryset_for_staff_without_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.assertEqual(len(queryset), 0)

    def test_staff_user_has_obj_lvl_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        for mother in Mother.objects.all():
            factory = ManagerFactory()
            primary_manager = factory.create('PrimaryStageManager')
            primary_manager.assign_user(content_type='mothers', obj=mother)

        self.assertEqual(len(queryset), 2)

    def test_staff_user_has_obj_lvl_perm_on_one_instance(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type='mothers', obj=mother)

        self.assertEqual(len(queryset), 1)

    def test_staff_user_has_model_view_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

    def test_staff_user_has_model_view_perm_on_diff_stage(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother_2 = Mother.objects.create(name='Mother 2')

        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT, finished=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        Stage.objects.create(mother=mother_2, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother_2, stage=Stage.StageChoices.FIRST_VISIT, finished=True)

        self.assertEqual(len(queryset), 2)
