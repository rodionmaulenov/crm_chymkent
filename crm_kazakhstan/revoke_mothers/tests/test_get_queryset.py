# from django.test import TestCase, RequestFactory
# from django.contrib.admin.sites import AdminSite
# from django.contrib.auth import get_user_model
# from django.db import models
#
# from mothers.models import Comment, Mother
# from revoke_mothers.admin import RevokeMotherAdmin
# from revoke_mothers.models import RevokeMother
#
# User = get_user_model()
# Comment: models
# Mother: models
#
#
# class GetQuerySetTest(TestCase):
#
#     def setUp(self):
#         self.site = AdminSite()
#         self.admin = RevokeMotherAdmin(RevokeMother, self.site)
#         self.factory = RequestFactory()
#         self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
#
#         # Create Mothers and Comments
#         self.mother_with_revoked_comment = Mother.objects.create(name='Mother 1')
#         Comment.objects.create(mother=self.mother_with_revoked_comment, banned=True)
#
#         self.mother_with_revoked_comment1 = Mother.objects.create(name='Mother 2')
#         Comment.objects.create(mother=self.mother_with_revoked_comment1, banned=True)
#
#         self.mother_without_revoked_comment = Mother.objects.create(name='Mother 3')
#         Comment.objects.create(mother=self.mother_without_revoked_comment, banned=False)
#
#     def test_get_queryset_excludes_revoked_comments(self):
#         request = self.factory.get('/')
#         request.user = self.user
#         queryset = self.admin.get_queryset(request)
#
#         self.assertEqual(len(queryset), 2)
#
#         # Check if mothers without revoked comments are not in queryset
#         self.assertNotIn(self.mother_without_revoked_comment, queryset)
