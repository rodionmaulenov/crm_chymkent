from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.http import HttpRequest
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.db import models

from mothers.admin import MotherAdmin
from mothers.models import Mother, Comment, Planned, Stage

Mother: models
Comment: models
Stage: models
Planned: models
User = get_user_model()


def add_session_to_request(request: HttpRequest) -> HttpRequest:
    """Adds session support to a RequestFactory generated request."""
    middleware = SessionMiddleware(get_response=lambda request: None)
    middleware.process_request(request)
    request.session.save()
    return request


def add_messages_to_request(request: HttpRequest) -> HttpRequest:
    """Adds message/alert support to a RequestFactory generated request."""
    request._messages = FallbackStorage(request)
    return request


class MakeRevokeTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username='user', password='user', is_staff=True)

        can_view_mother_permission = Permission.objects.get(codename='view_mother')
        self.revoke_mothers = Permission.objects.get(codename='revoke_mothers')

        self.staff_user.user_permissions.add(can_view_mother_permission)

        self.mother1 = Mother.objects.create(name='Mother 1', number='123', program='Test Program 1')
        self.mother2 = Mother.objects.create(name='Mother 2', number='456', program='Test Program 2')
        self.mother3 = Mother.objects.create(name='Mother 3', number='678', program='Test Program 3')

        Comment.objects.create(mother=self.mother1)
        Comment.objects.create(mother=self.mother2)
        Comment.objects.create(mother=self.mother3)

        admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, admin_site)

    def test_make_revoke_action_with_access(self):
        queryset = Mother.objects.all()
        request = HttpRequest()
        request = add_session_to_request(request)
        request = add_messages_to_request(request)

        comments_before = Comment.objects.filter(mother__in=queryset, revoked=True).count()
        self.mother_admin.make_revoke(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, revoked=True).count()

        self.assertGreater(comments_after, comments_before)

    def test_make_revoke_action_with_access_another_way(self):
        request = RequestFactory()
        request = request.post('/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        queryset = Mother.objects.all()

        comments_before = Comment.objects.filter(mother__in=queryset, revoked=True).count()
        self.mother_admin.make_revoke(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, revoked=True).count()

        self.assertGreater(comments_after, comments_before)

    def test_actions_with_permission(self):
        self.staff_user.user_permissions.add(self.revoke_mothers)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('make_revoke', actions)

    def test_actions_without_permission(self):
        self.staff_user.user_permissions.remove(self.revoke_mothers)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('make_revoke', actions)

    def test_request_actions_without_permission(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(reverse('admin:mothers_mother_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'make_revoke')

        self.client.logout()

    def test_request_actions_with_permission(self):
        self.client.force_login(self.staff_user)
        self.staff_user.user_permissions.add(self.revoke_mothers)
        response = self.client.post(reverse('admin:mothers_mother_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'make_revoke')

        self.client.logout()


class ChangeStageTest(TestCase):

    def setUp(self):
        self.super_user = User.objects.create_user(username='user', password='user', is_superuser=True)
        self.staff_user = User.objects.create_user(username='superuser', password='passworduser', is_staff=True)

        can_view_mother_permission = Permission.objects.get(codename='view_mother')
        self.transfer_on_first_visit = Permission.objects.get(codename='action_first_visit')

        self.staff_user.user_permissions.add(can_view_mother_permission)

        admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, admin_site)

        self.factory = RequestFactory()

    def test_mothers_move_on_first_visit_stage(self):
        request = self.factory
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        mother1 = Mother.objects.create(name='Mother 1', number='123', program='Test Program 1')
        mother2 = Mother.objects.create(name='Mother 2', number='456', program='Test Program 2')

        Planned.objects.create(mother=mother1, plan=Planned.PlannedChoices.TAKE_TESTS)
        Planned.objects.create(mother=mother2, plan=Planned.PlannedChoices.TAKE_TESTS)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(2, len(queryset))

        self.mother_admin.first_visit_stage(request, queryset)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(0, len(queryset))

        self.assertTrue(mother1.stage.stage == Stage.StageChoices.PRIMARY)
        self.assertTrue(mother2.stage.stage == Stage.StageChoices.PRIMARY)

    def test_raise_integrityerror(self):
        request = self.factory
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        mother1 = Mother.objects.create(name='Mother 1', number='123', program='Test Program 1')
        mother2 = Mother.objects.create(name='Mother 2', number='456', program='Test Program 2')
        mother3 = Mother.objects.create(name='Mother 3', number='4567', program='Test Program 3')

        Planned.objects.create(mother=mother1, plan=Planned.PlannedChoices.TAKE_TESTS)
        Planned.objects.create(mother=mother2, plan=Planned.PlannedChoices.TAKE_TESTS)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(3, len(queryset))

        self.mother_admin.first_visit_stage(request, queryset)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(1, len(queryset))

        self.assertTrue(mother1.stage.stage == Stage.StageChoices.PRIMARY)
        self.assertTrue(mother2.stage.stage == Stage.StageChoices.PRIMARY)

        with self.assertRaises(Mother.stage.RelatedObjectDoesNotExist):
            x = mother3.stage.stage

    def test_actions_with_permission(self):
        self.staff_user.user_permissions.add(self.transfer_on_first_visit)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('first_visit_stage', actions)

    def test_actions_without_permission(self):
        self.staff_user.user_permissions.remove(self.transfer_on_first_visit)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('first_visit_stage', actions)

    def test_actions_superuser_permission_success(self):
        request = HttpRequest()
        request.user = self.super_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('first_visit_stage', actions)
