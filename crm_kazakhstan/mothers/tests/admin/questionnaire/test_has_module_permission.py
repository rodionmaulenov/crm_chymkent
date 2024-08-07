from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm
from mothers.admin.questionnaire import QuestionnaireAdmin
from mothers.models import Mother, ScheduledEvent
from django.contrib import admin

User = get_user_model()


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = QuestionnaireAdmin(Mother, admin.site)
        self.user1 = User.objects.create_user(username='user1', password='password1', timezone='UTC')

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

    def test_has_module_permission_with_custom_perm(self):
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        # Create timezone-aware ScheduledEvent instances
        aware_datetime1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))

        self.scheduled_event1 = ScheduledEvent.objects.create(mother=self.mother1, scheduled_time=aware_datetime1,
                                                              is_completed=True)
        self.scheduled_event2 = ScheduledEvent.objects.create(mother=self.mother2, scheduled_time=aware_datetime2,
                                                              is_completed=True)

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertTrue(has_module_permission)

    def test_has_module_permission_with_custom_perm_with_incomplete_event(self):
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        # Create timezone-aware ScheduledEvent instances
        aware_datetime1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))

        self.scheduled_event1 = ScheduledEvent.objects.create(mother=self.mother1, scheduled_time=aware_datetime1,
                                                              is_completed=False)
        self.scheduled_event2 = ScheduledEvent.objects.create(mother=self.mother2, scheduled_time=aware_datetime2,
                                                              is_completed=False)

        # Set permissions for user1
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertFalse(has_module_permission)

    def test_has_module_permission_with_base_view_questionnaire_and_full_queryset(self):
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        # Create timezone-aware ScheduledEvent instances
        aware_datetime1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))

        self.scheduled_event1 = ScheduledEvent.objects.create(mother=self.mother1, scheduled_time=aware_datetime1,
                                                              is_completed=True)
        self.scheduled_event2 = ScheduledEvent.objects.create(mother=self.mother2, scheduled_time=aware_datetime2,
                                                              is_completed=True)

        permission = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user1.user_permissions.add(permission)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertTrue(has_module_permission)

    def test_has_module_permission_with_base_view_questionnaire_and_empty_queryset(self):
        self.mother1 = Mother.objects.create(name="Mother1")
        self.mother2 = Mother.objects.create(name="Mother2")
        # Create timezone-aware ScheduledEvent instances
        aware_datetime1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))

        self.scheduled_event1 = ScheduledEvent.objects.create(mother=self.mother1, scheduled_time=aware_datetime1,
                                                              is_completed=False)
        self.scheduled_event2 = ScheduledEvent.objects.create(mother=self.mother2, scheduled_time=aware_datetime2,
                                                              is_completed=False)

        permission = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user1.user_permissions.add(permission)

        request = self.factory.get('/')
        request.user = self.user1

        has_module_permission = self.admin_instance.has_module_permission(request)
        self.assertFalse(has_module_permission)
