from freezegun import freeze_time

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


class WhenCreatedTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              timezone='Europe/Kiev')

    @freeze_time('01.04.2024')
    def test_what_display(self):
        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment')
        request = self.factory.get('/')
        request.user = self.staff_user

        self.inline_ban.get_queryset(request)
        created = self.inline_ban.when_created(ban)

        self.assertEqual(created, '04.01.2024')
