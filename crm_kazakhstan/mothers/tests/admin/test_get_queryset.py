from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Comment, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Comment: models
Stage: models
Mother: models


class GetQuerySetTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_Mother_has_relate_Stage_instance_finished_equal_True(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=True)

        self.assertEqual(len(queryset), 1)

    def test_Mother_has_relate_Stage_instance_finished_equal_False(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=False)

        self.assertEqual(len(queryset), 0)

    def test_Mother_has_relate_Comment_instance_banned_equal_False(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=False)

        self.assertEqual(len(queryset), 1)

    def test_Mother_has_relate_Comment_instance_banned_equal_True(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=True)

        self.assertEqual(len(queryset), 0)

    def test_Mother_has_relate_Comment_instance_banned_equal_False_and_Stage_instance_finished_equal_True(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=False)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=True)

        self.assertEqual(len(queryset), 1)

    def test_Mother_has_relate_Comment_instance_banned_equal_False_and_Stage_instance_finished_equal_False(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=False)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=False)

        self.assertEqual(len(queryset), 0)

    def test_Mother_has_relate_Comment_instance_banned_equal_True_and_Stage_instance_finished_equal_True(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=True)

        self.assertEqual(len(queryset), 0)

    def test_Mother_has_relate_Comment_instance_banned_equal_True_and_Stage_instance_finished_equal_False(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother, banned=True)
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY,
                             finished=True)

        self.assertEqual(len(queryset), 0)

    def test_Mother_has_not_relate_Stage_instance_and_comment_instance(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        Mother.objects.create(name='Mother 1')

        self.assertEqual(len(queryset), 1)
