from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from mothers.inlines import BanInline
from mothers.models import Ban, Mother

User = get_user_model()
Mother: models
Ban: models


class DisplayBannedTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True,
                                              timezone='Europe/Kiev')

    def test_display_banned_false(self):
        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment')

        banned = self.inline_ban.display_banned(ban)
        self.assertEqual(
            '<img src="/static/mothers/icons/red_check_mark.jpg" alt="Failure" style="width: 18px; height: 20px;"/>',
            banned)

    def test_display_banned_true(self):
        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment', banned=True)

        banned = self.inline_ban.display_banned(ban)
        self.assertEqual(
            '<img src="/static/mothers/icons/green_check_mark.jpg" alt="Success" style="width: 18px; height: 20px;"/>',
            banned)
