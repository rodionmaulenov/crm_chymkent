from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.db.models import Q
from mothers.filters.applications import UsersObjectsFilter
from mothers.models import Mother
from mothers.admin import MotherAdmin
from mothers.services_main import assign_user

User = get_user_model()


class CustomUserAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.mother_admin_instance = MotherAdmin(Mother, admin.site)
        self.user1 = User.objects.create_user(username='user1', password='password1', country='UZBEKISTAN')
        self.user2 = User.objects.create_user(username='user2', password='password2', country='KYRGYZSTAN')
        self.user3 = User.objects.create_user(username='user3', password='password3')  # No country

        # Create test Mother instances
        self.mother1 = Mother.objects.create(name="Mother1", age=None)
        self.mother2 = Mother.objects.create(name="Mother2", residence=None)
        self.mother3 = Mother.objects.create(name="Mother3", height=None)
        self.mother4 = Mother.objects.create(name="Mother4", weight=None)
        self.mother5 = Mother.objects.create(name="Mother5", caesarean=None)
        self.mother6 = Mother.objects.create(name="Mother6", children=None)
        self.mother7 = Mother.objects.create(name="Mother7", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)

        self.queryset = Mother.objects.filter(
            Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
            Q(caesarean__isnull=True) | Q(children__isnull=True)
        )

    def test_lookups(self):
        request = self.factory.get('/')
        request.user = self.user1
        assign_user(request, self.mother_admin_instance, self.mother1)
        filter_ = UsersObjectsFilter(request, {}, Mother, self.mother_admin_instance)

        lookups = filter_.lookups(request, self.mother_admin_instance)
        expected_lookups = [('user1', 'Uzbekistan user1')]
        self.assertEqual(expected_lookups, lookups)

        request = self.factory.get('/')
        request.user = self.user2
        assign_user(request, self.mother_admin_instance, self.mother2)
        filter_ = UsersObjectsFilter(request, {}, Mother, self.mother_admin_instance)

        lookups = filter_.lookups(request, self.mother_admin_instance)
        expected_lookups = [('user1', 'Uzbekistan user1'), ('user2', 'Kyrgyzstan user2')]
        self.assertEqual(expected_lookups, lookups)

        request = self.factory.get('/')
        request.user = self.user3
        filter_ = UsersObjectsFilter(request, {}, Mother, self.mother_admin_instance)

        lookups = filter_.lookups(request, self.mother_admin_instance)
        expected_lookups = [('user1', 'Uzbekistan user1'), ('user2', 'Kyrgyzstan user2')]
        self.assertEqual(expected_lookups, lookups)

    def test_queryset(self):
        request = self.factory.get('/')
        request.user = self.user1
        assign_user(request, self.mother_admin_instance, self.mother1)
        filter_ = UsersObjectsFilter(request, {'username': 'user1'}, Mother, self.mother_admin_instance)

        queryset = filter_.queryset(request, self.queryset)
        expected_queryset = 1
        self.assertEqual(expected_queryset, queryset.count())

        request = self.factory.get('/')
        request.user = self.user2
        assign_user(request, self.mother_admin_instance, self.mother2)
        assign_user(request, self.mother_admin_instance, self.mother3)
        filter_ = UsersObjectsFilter(request, {'username': 'user2'}, Mother, self.mother_admin_instance)

        queryset = filter_.queryset(request, self.queryset)
        expected_queryset = 2
        self.assertEqual(expected_queryset, queryset.count())

        request = self.factory.get('/')
        request.user = self.user3
        filter_ = UsersObjectsFilter(request, {'username': 'user3'}, Mother, self.mother_admin_instance)

        queryset = filter_.queryset(request, self.queryset)
        expected_queryset = 0
        self.assertEqual(expected_queryset, queryset.count())
