from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models

from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class GetQuerysetTest(TestCase):
    def setUp(self):
        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.document_admin = DocumentProxyAdmin(DocumentProxy, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_superuser_has_queryset(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.assertEqual(len(queryset), 2)

    def test_superuser_has_mothers_on_another_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        self.assertEqual(len(queryset), 2)

    def test_superuser_mix_stage(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        self.assertEqual(len(queryset), 2)

    def test_empty_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.document_admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)

    def test_staff_without_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.assertEqual(len(queryset), 0)

    def test_staff_user_has_custom_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        for mother in Mother.objects.all():
            factory = ManagerFactory()
            primary_manager = factory.create('PrimaryStageManager')
            primary_manager.assign_user(content_type=self.mother_admin, obj=mother, user=self.staff_user)

        self.assertEqual(len(queryset), 2)

    def test_staff_user_has_custom_perm_on_primary_stage(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY, finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type='mothers', obj=mother)

        self.assertEqual(len(queryset), 1)

    def test_staff_user_has_custom_perm_on_first_visit(self):
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type='mothers', obj=mother, user=self.staff_user)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

        staff_user2 = User.objects.create(username='staff_user2', password='password', is_staff=True,
                                          stage=Stage.StageChoices.FIRST_VISIT)
        primary_manager = factory.create('FirstVisitStageManager')
        primary_manager.assign_user(content_type='mothers', obj=mother2, user=staff_user2)

        request = self.factory.get('/')
        request.user = staff_user2
        queryset2 = self.document_admin.get_queryset(request)
        self.assertTrue(queryset2.first().name == 'Mother 2')

    def test_staff_user_has_base_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        view_permission = Permission.objects.get(codename='view_documentproxy')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

    def test_staff_user_has_base_perm_on_diff_stage(self):
        view_permission = Permission.objects.get(codename='view_documentproxy')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.document_admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        mother_2 = Mother.objects.create(name='Mother 2')

        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT, finished=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        Stage.objects.create(mother=mother_2, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=mother_2, stage=Stage.StageChoices.FIRST_VISIT, finished=True)

        self.assertEqual(len(queryset), 2)
