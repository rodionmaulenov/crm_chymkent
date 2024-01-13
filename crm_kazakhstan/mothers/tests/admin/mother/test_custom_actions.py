from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.admin import MotherAdmin
from mothers.models import Mother, Comment, Planned, Stage

Mother: models
Comment: models
Stage: models
Planned: models
User = get_user_model()


class BannedActionCustomMethodTest(TestCase):
    def setUp(self):
        admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, admin_site)
        self.request_factory = RequestFactory()

    def test_move_to_ban_list_when_Comment_description_is_not_empty(self):
        request = self.request_factory.post('/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        mother1 = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother1, description='it is a man')

        queryset = Mother.objects.all()

        comments_before = Comment.objects.filter(mother__in=queryset, banned=True).count()
        self.mother_admin.banned(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, banned=True).count()

        self.assertGreater(comments_after, comments_before)

    def test_move_to_ban_list_when_Comment_description_is_empty(self):
        request = self.request_factory.post('/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        mother1 = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother1)

        queryset = Mother.objects.all()

        comments_before = Comment.objects.filter(mother__in=queryset, banned=True).count()
        self.mother_admin.banned(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, banned=True).count()

        self.assertEqual(comments_after, comments_before)

    def test_move_to_ban_list_when_Comment_description_exists_and_banned_already_True(self):
        request = self.request_factory.post('/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        mother1 = Mother.objects.create(name='Mother 1')
        Comment.objects.create(mother=mother1, description='it is a man', banned=True)

        queryset = Mother.objects.all()

        comments_before = Comment.objects.filter(mother__in=queryset, banned=True).count()
        self.mother_admin.banned(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, banned=True).count()

        self.assertEqual(comments_after, comments_before)


class FirstVisitStageCustomActionMethodTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        user = User.objects.create_superuser('testname', 'email@gmail.com', 'password')
        self.request = self.factory.get('/')
        setattr(self.request, 'session', 'session')
        setattr(self.request, '_messages', FallbackStorage(self.request))
        self.request.user = user

        admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, admin_site)

    def test_move_on_first_visit_stage_when_Planned_plan_equal_TAKE_TESTS_and_finished_False(self):
        mother1 = Mother.objects.create(name='Mother 1')
        Planned.objects.create(mother=mother1, plan=Planned.PlannedChoices.TAKE_TESTS, finished=False)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        self.mother_admin.first_visit_stage(self.request, queryset)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(0, len(queryset))

        self.assertTrue(mother1.stage_set.last().stage == Stage.StageChoices.PRIMARY)

    def test_move_on_first_visit_stage_when_Planned_plan_equal_TAKE_TESTS_and_finished_True(self):
        mother1 = Mother.objects.create(name='Mother 1')
        Planned.objects.create(mother=mother1, plan=Planned.PlannedChoices.TAKE_TESTS, finished=True)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        self.mother_admin.first_visit_stage(self.request, queryset)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        with self.assertRaises(AttributeError):
            self.assertTrue(mother1.stage_set.last().stage == Stage.StageChoices.PRIMARY)

    def test_move_on_first_visit_stage_when_Planned_plan_empty_and_finished_False(self):
        mother1 = Mother.objects.create(name='Mother 1')
        Planned.objects.create(mother=mother1, finished=False)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        self.mother_admin.first_visit_stage(self.request, queryset)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        with self.assertRaises(AttributeError):
            self.assertTrue(mother1.stage_set.last().stage == Stage.StageChoices.PRIMARY)

    def test_move_on_first_visit_without_Planned_instance(self):
        mother1 = Mother.objects.create(name='Mother 1')
        Planned.objects.create(mother=mother1, finished=False)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        self.mother_admin.first_visit_stage(self.request, queryset)

        queryset = self.mother_admin.get_queryset(self.request)
        self.assertEqual(1, len(queryset))

        with self.assertRaises(AttributeError):
            self.assertTrue(mother1.stage_set.last().stage == Stage.StageChoices.PRIMARY)

