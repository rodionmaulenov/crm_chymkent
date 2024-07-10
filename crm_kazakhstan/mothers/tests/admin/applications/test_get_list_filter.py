from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib import admin

from mothers.admin import MotherAdmin
from mothers.filters.applications import DayOfWeekFilter, UsersObjectsFilter
from mothers.models import Mother
from mothers.services_main import assign_user

User = get_user_model()


class MotherAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.admin_instance = MotherAdmin(Mother, admin.site)

    def test_get_list_filter_single_permission(self):
        view_permission = Permission.objects.get(codename='view_mother')
        self.user1.user_permissions.add(view_permission)

        Mother.objects.create(name="Mother1", age=None)

        request = self.factory.get('/')
        request.user = self.user1

        filters = self.admin_instance.get_list_filter(request)

        self.assertEqual(filters, [DayOfWeekFilter, UsersObjectsFilter])

    def test_get_list_filter_no_queryset(self):
        # Simulate request for user3
        request = self.factory.get('/')
        request.user = self.user3

        filters = self.admin_instance.get_list_filter(request)
        self.assertEqual(filters, [])

    def test_get_list_filter_multiple_permissions(self):
        mother = Mother.objects.create(name="Mother1")

        # Assign additional permission to user1
        change_mother = Permission.objects.get(codename='change_mother')
        self.user2.user_permissions.add(change_mother)
        view_mother = Permission.objects.get(codename='view_mother')
        self.user2.user_permissions.add(view_mother)

        request = self.factory.get('/')
        request.user = self.user2
        assign_user(request, self.admin_instance, mother)

        filters = self.admin_instance.get_list_filter(request)
        self.assertEqual(filters, [DayOfWeekFilter])

    def test_get_list_super_user(self):
        Mother.objects.create(name="Mother1")

        request = self.factory.get('/')
        request.user = self.superuser

        filters = self.admin_instance.get_list_filter(request)
        self.assertEqual(filters, [DayOfWeekFilter])
