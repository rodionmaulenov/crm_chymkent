from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Comment, Stage
from mothers.admin import PrimaryVisitAdmin

User = get_user_model()
Comment: models
Stage: models
Mother: models


class GetQuerySetTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = PrimaryVisitAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        # Create Mothers and Comments
        self.mother_without_revoked_comment = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=self.mother_without_revoked_comment, revoked=False)
        Stage.objects.create(mother=self.mother_without_revoked_comment, stage=Stage.StageChoices.PRIMARY)

        self.mother_with_revoked_comment2 = Mother.objects.create(name='Mother 2')
        Comment.objects.create(mother=self.mother_with_revoked_comment2, revoked=True)

        self.mother_with_revoked_comment3 = Mother.objects.create(name='Mother 3')
        Comment.objects.create(mother=self.mother_with_revoked_comment3, revoked=True)

        self.mother_with_revoked_comment4 = Mother.objects.create(name='Mother 4')
        Comment.objects.create(mother=self.mother_with_revoked_comment4, revoked=True)
        Stage.objects.create(mother=self.mother_with_revoked_comment4, stage=Stage.StageChoices.PRIMARY)

        self.mother_without_revoked_comment5 = Mother.objects.create(name='Mother 5')
        Comment.objects.create(mother=self.mother_without_revoked_comment5, revoked=False)
        Stage.objects.create(mother=self.mother_without_revoked_comment5, stage=Stage.StageChoices.PRIMARY)

    def test_get_queryset_excludes_revoked_comments(self):
        request = self.factory.get('/')
        request.user = self.user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(2, len(queryset))
