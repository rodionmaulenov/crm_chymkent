from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from gmail_messages.admin import CustomUserAdmin
from gmail_messages.models import CustomUser


class CustomUserAdminTest(TestCase):
    def test_timezone_field_in_fieldsets(self):
        admin = CustomUserAdmin(CustomUser, AdminSite())
        timezone_exists = any('timezone' in fieldset[1]['fields'] for fieldset in admin.fieldsets)
        self.assertTrue(timezone_exists)

    def test_stage_field_in_fieldsets(self):
        admin = CustomUserAdmin(CustomUser, AdminSite())
        timezone_exists = any('stage' in fieldset[1]['fields'] for fieldset in admin.fieldsets)
        self.assertTrue(timezone_exists)