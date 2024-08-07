from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time
from django.contrib.admin.sites import AdminSite
from mothers.admin import ShortPlanAdmin
from mothers.filters.short_plan import NewEventOccursFilter
from mothers.models import Mother, ScheduledEvent

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm

User = get_user_model()


class NewEventOccursFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = ShortPlanAdmin(Mother, AdminSite())
        self.user = User.objects.create_user(username='user', password='password', timezone='UTC')

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
    def test_filter_with_new_event(self):
        scheduled_time_past = timezone.make_aware(timezone.datetime(2024, 7, 19, 15, 0, 0))
        scheduled_time_future = timezone.make_aware(timezone.datetime(2024, 7, 21, 15, 0, 0))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Event in the past',
            scheduled_time=scheduled_time_past,
            is_completed=False
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Event in the future',
            scheduled_time=scheduled_time_future,
            is_completed=False
        )

        request = self.factory.get('/')
        request.user = self.user

        filter_instance = NewEventOccursFilter(request, {'an_event_occurred': 'new_event'}, Mother, self.admin_instance)
        queryset = filter_instance.queryset(request, Mother.objects.all())

        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)

    @freeze_time("2024-07-20 15:00:00")
    def test_filter_without_new_event(self):
        scheduled_time_future = timezone.make_aware(timezone.datetime(2024, 7, 21, 15, 0, 0))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Event in the future',
            scheduled_time=scheduled_time_future,
            is_completed=False
        )

        request = self.factory.get('/')
        request.user = self.user

        filter_instance = NewEventOccursFilter(request, {'an_event_occurred': 'new_event'}, Mother, self.admin_instance)
        queryset = filter_instance.queryset(request, Mother.objects.all())

        self.assertNotIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)
