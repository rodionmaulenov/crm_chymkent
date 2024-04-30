from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from ban.inlines import BanInline
from ban.models import Ban

from mothers.models import Mother

User = get_user_model()
Mother: models
Ban: models


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_super_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        state = Ban.objects.create(mother=mother, comment='comment')
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.inline_ban.has_view_permission(request, state)

        self.assertTrue(view)

    def test_staff_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        state = Ban.objects.create(mother=mother, comment='comment')
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.inline_ban.has_view_permission(request, state)

        self.assertTrue(view)
