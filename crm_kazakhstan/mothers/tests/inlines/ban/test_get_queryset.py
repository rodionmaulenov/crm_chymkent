from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from mothers.inlines import BanInline
from mothers.models import Ban

User = get_user_model()
Mother: models
Ban: models


class GetQuerysetTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_assign_request(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        self.assertFalse(hasattr(self.inline_ban, 'request'))
        self.inline_ban.get_queryset(request)
        self.assertTrue(hasattr(self.inline_ban, 'request'))

