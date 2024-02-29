from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from mothers.models import Ban, Mother
from mothers.admin import BanAdmin

User = get_user_model()

Ban: models
Mother: models


class SaveModelTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.user = User.objects.create_superuser(username='admin', password='password')

    # def test_add_ban_with_perms_change_and_view(self):
    #     mother = Mother.objects.create(name='Mother')
    #     obj = Ban(mother=mother, comment='comment')
    #     self.assertIsNone(obj.pk)
    #     request = self.factory.get('/')
    #     request.user = self.user
    #
    #     form = self.admin.get_form(request)
    #     self.admin.save_model(request, obj, form, change=False)
    #
    #     obj.refresh_from_db()
    #     self.assertIsNotNone(obj.pk)
    #
    #     for perm in ['view_ban', 'change_ban', 'add_ban']:
    #         self.assertTrue(self.user.has_perm(perm), obj)