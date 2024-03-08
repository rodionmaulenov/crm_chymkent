from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from mothers.inlines import BanInline
from mothers.models import Ban, Mother

User = get_user_model()
Mother: models
Ban: models


class WhenCreatedTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True,
                                              timezone='Europe/Kiev')

    def test_what_display(self):
        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment')
        request = self.factory.get('/')
        request.user = self.staff_user

        self.inline_ban.get_queryset(request)
        created = self.inline_ban.when_created(ban)

        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment')
        request = self.factory.get('/')
        request.user = User.objects.create(username='staffuser1', password='password', is_staff=True)

        self.inline_ban.get_queryset(request)
        created_utc = self.inline_ban.when_created(ban)

        self.assertGreater(created, created_utc)
