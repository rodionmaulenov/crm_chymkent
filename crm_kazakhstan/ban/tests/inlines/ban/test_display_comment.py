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


class DisplayCommentTest(TestCase):
    def setUp(self):
        self.inline_ban = BanInline(Ban, admin.site)
        self.factory = RequestFactory()

        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_what_display(self):
        mother = Mother.objects.create(name='mother')
        ban = Ban.objects.create(mother=mother, comment='comment')

        comment = self.inline_ban.display_comment(ban)
        self.assertEqual(comment, '<strong>COMMENT</strong>')
