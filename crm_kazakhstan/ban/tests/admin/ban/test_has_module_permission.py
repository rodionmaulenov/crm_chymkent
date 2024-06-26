from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from mothers.models import Stage

from ban.admin import BanAdmin
from ban.models import Ban

User = get_user_model()


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_superuser_has_not_access(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_stuff_user_has_not_access(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)
