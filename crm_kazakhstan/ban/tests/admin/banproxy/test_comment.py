from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from ban.admin import BanProxyAdmin
from ban.models import BanProxy

from mothers.models import Mother, Stage

from ban.models import Ban

User = get_user_model()
Mother: models
Ban: models
Stage: models


class CommentTest(TestCase):
    def setUp(self):
        self.admin = BanProxyAdmin(BanProxy, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=self.mother, comment='some reason', banned=True)

        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_comment(self):
        comment = self.admin.comment(self.mother)
        self.assertEqual(comment, 'some reason')

    def test_no_comment(self):
        mother = Mother.objects.create(name='mother1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='', banned=True)

        comment = self.admin.comment(mother)
        self.assertEqual(comment, '')
