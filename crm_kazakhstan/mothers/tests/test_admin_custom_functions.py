# from django.test import TestCase
# from django.contrib.admin.sites import AdminSite
# from django.db import models
#
# from mothers.models import Mother
# from mothers.admin import MotherAdmin
# from documents.models import Document
#
#
# Mother: models
# Document: models
#
#
# class MotherAdminTest(TestCase):
#     def setUp(self):
#         self.mother = Mother.objects.create(
#             name='Test Mother',
#             number='123',
#             program='Test Program',
#             residence='Test Residence',
#             height_and_weight='Test Height and Weight',
#         )
#
#         self.mother2 = Mother.objects.create(
#             name='Test2 Mother',
#             number='1234',
#             program='Test2 Program',
#             residence='Test2 Residence',
#             height_and_weight='Test2 Height and Weight',
#         )
#
#         Document.objects.create(mother=self.mother, name='свидетельство ребёнка')
#         Document.objects.create(mother=self.mother, name='cвидетельство мамы')
#         Document.objects.create(mother=self.mother, name='нет судимости')
#         Document.objects.create(mother=self.mother, name='нарколог')
#         Document.objects.create(mother=self.mother, name='психиатр')
#         Document.objects.create(mother=self.mother, name='не в браке')
#         Document.objects.create(mother=self.mother, name='загранпаспорт')
#
#         self.admin_site = AdminSite()
#         self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)
#
#     def test_formatted_document_list_all_documents_in_list(self):
#         formatted_document_list = self.mother_admin_instance.formatted_document_list(self.mother)
#
#         self.assertIn("/static/admin/img/icon-yes.svg", formatted_document_list)
#         self.assertIn('width: 20px; height: 20px;', formatted_document_list)
#
#     def test_formatted_document_list_not_all_documents_in_list(self):
#         formatted_document_list = self.mother_admin_instance.formatted_document_list(self.mother2)
#
#         # Check that the output contains the <select> tag
#         self.assertIn('<div><select><option>', formatted_document_list)
