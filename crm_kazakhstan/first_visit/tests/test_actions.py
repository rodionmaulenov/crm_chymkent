# from django.contrib.messages.storage.fallback import FallbackStorage
# from django.test import TestCase, RequestFactory
# from django.contrib.admin.sites import AdminSite
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Permission
# from django.db import models
# from django.utils import timezone
#
# from first_visit.admin import PrimaryVisitAdmin
# from mothers.models import Mother, Planned, Stage
#
# User = get_user_model()
# Mother: models
# Planned: models
# Stage: models
#
#
# class OnPrimaryStage(TestCase):
#     def setUp(self):
#         self.staff_user = User.objects.create_user(username='user', password='user', is_staff=True)
#         self.super_user = User.objects.create_user(username='user1', password='user', is_staff=True, is_superuser=True)
#
#         can_view_mother_permission = Permission.objects.get(codename='view_mother')
#         self.move_on_primary_stage = Permission.objects.get(codename='action_on_primary_stage')
#
#         self.staff_user.user_permissions.add(can_view_mother_permission)
#
#         mother2 = Mother.objects.create(name='Mother 2', number='456', program='Test Program 2')
#         mother3 = Mother.objects.create(name='Mother 3', number='678', program='Test Program 3')
#
#         Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)
#         Stage.objects.create(mother=mother3, stage=Stage.StageChoices.PRIMARY)
#
#         Planned.objects.create(
#             mother=mother3,
#             plan=Planned.PlannedChoices.TAKE_TESTS,
#             scheduled_date=timezone.datetime(2023, 12, 12, tzinfo=timezone.utc).date()
#         )
#
#         admin_site = AdminSite()
#         self.primary_visit_admin = PrimaryVisitAdmin(Mother, admin_site)
#
#         self.request_factory = RequestFactory()
#
#     def test_go_on_primary_stage(self):
#         mother1 = Mother.objects.create(name='Mother 1', number='123', program='Test Program 1')
#         Stage.objects.create(mother=mother1, stage=Stage.StageChoices.PRIMARY)
#         Planned.objects.create(
#             mother=mother1,
#             plan=Planned.PlannedChoices.TAKE_TESTS,
#             note='not come on tests',
#             scheduled_date=timezone.datetime(2023, 12, 12, tzinfo=timezone.utc).date()
#         )
#         request = self.request_factory.get('/')
#         request.user = self.staff_user
#         request.session = 'session'
#         request._messages = FallbackStorage(request)
#
#         before_queryset = self.primary_visit_admin.get_queryset(request)
#         self.assertEqual(3, len(before_queryset))
#
#         self.primary_visit_admin.on_primary_stage(request, before_queryset)
#
#         after_queryset = self.primary_visit_admin.get_queryset(request)
#
#         self.assertEqual(2, len(after_queryset))
#
#     def test_without_go_on_primary_stage(self):
#         request = self.request_factory.get('/')
#         request.user = self.staff_user
#         request.session = 'session'
#         request._messages = FallbackStorage(request)
#
#         before_queryset = self.primary_visit_admin.get_queryset(request)
#         self.assertEqual(2, len(before_queryset))
#
#         self.primary_visit_admin.on_primary_stage(request, before_queryset)
#
#         after_queryset = self.primary_visit_admin.get_queryset(request)
#
#         self.assertEqual(2, len(after_queryset))
#
#     def test_actions_on_primary_stage_with_staff_user_permission(self):
#         self.staff_user.user_permissions.add(self.move_on_primary_stage)
#         request = self.request_factory.get('/')
#         request.user = self.staff_user
#
#         actions = self.primary_visit_admin.get_actions(request)
#         self.assertIn('on_primary_stage', actions)
#
#     def test_actions_on_primary_stage_without_staff_user_permission(self):
#         request = self.request_factory.get('/')
#         request.user = self.staff_user
#
#         actions = self.primary_visit_admin.get_actions(request)
#         self.assertNotIn('on_primary_stage', actions)
#
#     def test_actions_on_primary_super_user_permission(self):
#         request = self.request_factory.get('/')
#         request.user = self.super_user
#
#         actions = self.primary_visit_admin.get_actions(request)
#         self.assertIn('on_primary_stage', actions)
