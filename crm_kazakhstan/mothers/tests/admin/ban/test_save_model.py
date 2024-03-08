from guardian.shortcuts import get_perms

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

        self.staff_user = User.objects.create(username='admin', password='password', is_staff=True)

    def test_when_add_is_assigned_obj_perm_view(self):
        mother = Mother.objects.create(name='Mother')
        obj = Ban(mother=mother, comment='comment')
        self.assertIsNone(obj.pk)

        request = self.factory.get('/')
        request.user = self.staff_user

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        self.assertIsNotNone(obj.pk)

        self.assertEqual(get_perms(self.staff_user, obj), ['view_ban'])

