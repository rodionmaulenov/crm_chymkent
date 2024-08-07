from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm
from freezegun import freeze_time
from mothers.admin import ShortPlanAdmin
from mothers.models import Mother, ScheduledEvent
from django.contrib import admin

User = get_user_model()


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = ShortPlanAdmin(Mother, admin.site)
        self.user1 = User.objects.create_user(username='user1', password='password1', timezone='UTC')

        # Create test Mother instances
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother3 = Mother.objects.create(name="Mother3", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)

    @staticmethod
    def set_custom_permission(user, obj):
        model_name = obj.__class__.__name__.lower()
        codename = f'{model_name}_{user.username}'
        content_type = ContentType.objects.get_for_model(obj)
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=f'Can access {model_name} {user.username}',
            content_type=content_type,
        )
        assign_perm(permission, user, obj)

    @staticmethod
    def remove_custom_permission(user, obj):
        model_name = obj.__class__.__name__.lower()
        codename = f'{model_name}_{user.username}'
        remove_perm(codename, user, obj)

    @freeze_time("2024-07-20 15:00:00")
    def test_has_module_permission_with_custom_perm(self):
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 27, 15, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 14, 59, 59))

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

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=True
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=True
        )

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertTrue(has_module_permission)

    @freeze_time("2024-07-20 15:00:00")
    def test_has_module_permission_with_custom_perm_not_queryset(self):
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 14, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 27, 15, 1, 0))

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

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertFalse(has_module_permission)

    @freeze_time("2024-07-20 15:00:00")
    def test_has_module_permission_with_base_view_short_plan_and_full_queryset(self):
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 9, 21, 15, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 27, 15, 1, 0))

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

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=True
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=True
        )

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        permission = Permission.objects.get(codename='view_shortplan')
        # Add the permission to the user
        self.user1.user_permissions.add(permission)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertTrue(has_module_permission)

    def test_has_module_permission_with_base_view_questionnaire_and_empty_queryset(self):
        scheduled_time_mother1 = timezone.make_aware(timezone.datetime(2024, 7, 28, 15, 0, 0))
        scheduled_time_mother2 = timezone.make_aware(timezone.datetime(2024, 7, 19, 15, 1, 0))

        ScheduledEvent.objects.create(
            mother=self.mother1,
            note='Completed Event',
            scheduled_time=scheduled_time_mother1,
            is_completed=True
        )
        ScheduledEvent.objects.create(
            mother=self.mother2,
            note='Incomplete Event',
            scheduled_time=scheduled_time_mother2,
            is_completed=False
        )

        permission = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user1.user_permissions.add(permission)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertFalse(has_module_permission)
