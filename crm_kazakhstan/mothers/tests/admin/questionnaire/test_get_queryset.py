from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm, remove_perm
from mothers.admin.questionnaire import QuestionnaireAdmin
from mothers.models import Mother, ScheduledEvent
from django.contrib import admin
from django.utils import timezone

User = get_user_model()


class GetQuerysetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = QuestionnaireAdmin(Mother, admin.site)
        self.user1 = User.objects.create_user(username='user1', password='password1', timezone='UTC')
        self.user2 = User.objects.create_user(username='user2', password='password2', timezone='UTC')

        # Create test Mother instances
        self.mother1 = Mother.objects.create(name="Mother1", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother2 = Mother.objects.create(name="Mother2", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother3 = Mother.objects.create(name="Mother3", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother4 = Mother.objects.create(name="Mother4", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother5 = Mother.objects.create(name="Mother5", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother6 = Mother.objects.create(name="Mother6", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        self.mother7 = Mother.objects.create(name="Mother7", age=30)

        # Create ScheduledEvent instances
        # Create timezone-aware ScheduledEvent instances
        aware_datetime1 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime2 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        aware_datetime3 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))

        self.scheduled_event1 = ScheduledEvent.objects.create(mother=self.mother1, scheduled_time=aware_datetime1,
                                                              is_completed=True)
        self.scheduled_event2 = ScheduledEvent.objects.create(mother=self.mother2, scheduled_time=aware_datetime2,
                                                              is_completed=False)
        self.scheduled_event3 = ScheduledEvent.objects.create(mother=self.mother3, scheduled_time=aware_datetime3,
                                                              is_completed=True)

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

    def test_get_queryset_user1_with_custom_perm(self):
        # Set permissions for user1
        self.mother9 = Mother.objects.create(name="Mother6", age=30, residence="New York", height="170", weight="65",
                                             caesarean=1, children=2)
        aware_datetime3 = timezone.make_aware(timezone.datetime(2024, 7, 20, 15, 0, 0))
        self.scheduled_event3 = ScheduledEvent.objects.create(mother=self.mother3, scheduled_time=aware_datetime3,
                                                              is_completed=True)
        self.set_custom_permission(self.user1, self.mother1)
        self.set_custom_permission(self.user1, self.mother2)
        self.set_custom_permission(self.user1, self.mother9)

        request = self.factory.get('/')
        request.user = self.user1

        queryset = self.admin_instance.get_queryset(request)

        # user1 should see mother1 (completed event) but not mother2 (incomplete event)
        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)
        self.assertNotIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

    def test_get_queryset_user2_with_one_base_perm(self):
        permission = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user2.user_permissions.add(permission)

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        # user2 should see all mothers except mother2 (incomplete event) and mother7 (null fields)
        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertIn(self.mother3, queryset)
        self.assertIn(self.mother4, queryset)
        self.assertIn(self.mother5, queryset)
        self.assertIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

    def test_get_queryset_user2_with_one_two_base_perm(self):
        view_application = Permission.objects.get(codename='view_mother')
        view_questionnaire = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user2.user_permissions.set([view_application, view_questionnaire])

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        # user2 should see all mothers except mother2 (incomplete event) and mother7 (null fields)
        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertIn(self.mother3, queryset)
        self.assertIn(self.mother4, queryset)
        self.assertIn(self.mother5, queryset)
        self.assertIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

    def test_get_queryset_user2_with_one_two_base_perm_and_one_not_view(self):
        view_application = Permission.objects.get(codename='change_mother')
        view_questionnaire = Permission.objects.get(codename='view_questionnaire')
        # Add the permission to the user
        self.user2.user_permissions.set([view_application, view_questionnaire])

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        # user2 should see no mothers as permissions are not view-only
        self.assertNotIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)
        self.assertNotIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

    def test_get_queryset_with_user1_permissions_removed(self):
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
        self.assertNotIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

        # Remove permissions for user1
        self.remove_custom_permission(self.user1, self.mother1)
        self.remove_custom_permission(self.user1, self.mother2)

        queryset = self.admin_instance.get_queryset(request)

        # user1 should not see any mothers as permissions are removed
        self.assertNotIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertNotIn(self.mother3, queryset)
        self.assertNotIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

    def test_different_users_in_the_same_time_has_different_instances(self):
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
        self.assertNotIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)

        # Set permissions for user2
        self.set_custom_permission(self.user2, self.mother3)
        self.set_custom_permission(self.user2, self.mother4)

        request = self.factory.get('/')
        request.user = self.user2

        queryset = self.admin_instance.get_queryset(request)

        # user2 should see mother3 (completed event) and mother4 (completed event)
        self.assertNotIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)
        self.assertIn(self.mother3, queryset)
        self.assertIn(self.mother4, queryset)
        self.assertNotIn(self.mother5, queryset)
        self.assertNotIn(self.mother6, queryset)
        self.assertNotIn(self.mother7, queryset)
