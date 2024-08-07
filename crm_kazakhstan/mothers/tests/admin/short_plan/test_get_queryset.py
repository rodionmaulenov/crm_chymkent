from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time
from mothers.admin import ShortPlanAdmin
from mothers.models import Mother, ScheduledEvent
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm

User = get_user_model()


class GetQuerysetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = ShortPlanAdmin(Mother, AdminSite())
        self.user1 = User.objects.create_user(username='user1', password='password1', timezone='UTC')
        self.user2 = User.objects.create_user(username='user2', password='password2', timezone='UTC')

        # Create test Mother instances
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother3 = Mother.objects.create(name="Mother3", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)

    def set_custom_permission(self, user, obj):
        model_name = obj.__class__.__name__.lower()
        codename = f'{model_name}_{user.username}'
        content_type = ContentType.objects.get_for_model(obj)
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=f'Can access {model_name} {user.username}',
            content_type=content_type,
        )
        assign_perm(permission, user, obj)

    def remove_custom_permission(self, user, obj):
        model_name = obj.__class__.__name__.lower()
        codename = f'{model_name}_{user.username}'
        remove_perm(codename, user, obj)

    @freeze_time("2024-07-20 15:00:00")
    def test_get_queryset_user1_with_custom_perm(self):
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 27, 15, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 14, 59, 59))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=True
        )

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=False
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=True
        )

        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=False
        )

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        request = self.factory.get('/')
        request.user = self.user1

        queryset = self.admin_instance.get_queryset(request)

        # user1 should see mother1 (completed event) but not mother2 (incomplete event)
        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)

    @freeze_time("2024-07-20 00:00:00")
    def test_get_queryset_user2_with_one_base_perm(self):
        permission = Permission.objects.get(codename='view_shortplan')
        # Add the permission to the user
        self.user2.user_permissions.add(permission)

        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 27, 0, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 19, 23, 59, 59))
        scheduled_time_mother3 = timezone.make_aware(timezone.datetime(2024, 7, 26, 23, 59, 59))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=True
        )

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=False
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=False
        )

        self.event_completed = ScheduledEvent.objects.create(
            mother=self.mother3,
            note='Completed Event',
            scheduled_time=scheduled_time_mother3,
            is_completed=True
        )

        self.event_completed = ScheduledEvent.objects.create(
            mother=self.mother3,
            note='Completed Event',
            scheduled_time=scheduled_time_mother3,
            is_completed=False
        )

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertIn(self.mother3, queryset)

    @freeze_time("2024-07-20 00:00:00")
    def test_get_queryset_user2_with_one_two_base_perm(self):
        view_application = Permission.objects.get(codename='view_mother')
        view_shortpaln = Permission.objects.get(codename='view_shortplan')

        self.user2.user_permissions.set([view_application, view_shortpaln])
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 27, 0, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 19, 23, 59, 59))
        scheduled_time_mother3 = timezone.make_aware(timezone.datetime(2024, 10, 26, 23, 59, 59))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=False
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=False
        )

        self.event_completed = ScheduledEvent.objects.create(
            mother=self.mother3,
            note='Completed Event',
            scheduled_time=scheduled_time_mother3,
            is_completed=False
        )

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertIn(self.mother3, queryset)

