from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from mothers.models import Condition
from mothers.admin import ConditionAdmin

User = get_user_model()


class HasModulePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        # Create a group
        self.primary_stage_group, created = Group.objects.get_or_create(name='primary_stage')

    def test_has_not_access_to_first_layer_site_mother_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_has_not_access_to_first_layer_site_mother_staff_user(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_has_not_access_to_first_layer_site_mother_staff_user_with_group(self):
        self.staff_user.groups.add(self.primary_stage_group)
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)
