# from datetime import datetime, time
#
# from django.test import TestCase, RequestFactory
# from django.contrib import admin
# from django.utils import timezone
# from django.db import models
#
# from first_visit.admin import PrimaryVisitAdmin
# from mothers.models import Mother, Planned, Stage
#
# Planned: models
# Mother: models
# Stage: models
#
#
# class ListDisplayPlannedFirstVisitTest(TestCase):
#     def setUp(self):
#         self.request_factory = RequestFactory()
#
#         self.first_visit_admin = PrimaryVisitAdmin(Mother, admin.site)
#
#         self.mother = Mother.objects.create(name='Test Mother')
#
#         Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)
#
#         Planned.objects.create(
#             mother=self.mother,
#             plan=Planned.PlannedChoices.FIRST_TEST,
#             scheduled_date=datetime(2023, 12, 27, tzinfo=timezone.utc),
#             scheduled_time=time(21, 20, 0)
#         )
#
#     def test_list_display(self):
#         request = self.request_factory.get('/')
#         request.GET = {'plan': 'tests'}
#
#         name, first_planned_visit, first_planned_visit_date = self.first_visit_admin.get_list_display(request)
#         self.assertTrue(name)
#         self.assertTrue(first_planned_visit)
#         self.assertTrue(first_planned_visit_date)
#
