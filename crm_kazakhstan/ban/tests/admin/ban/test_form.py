from django.test import TestCase, RequestFactory
from django.db import models

from mothers.forms import BanAdminForm
from mothers.models import Mother

Mother: models


class BanAdminFormTest(TestCase):

    def test_mother_filed_hide_when_add(self):
        mother = Mother.objects.create(name='name')
        data = {
            'mother': mother.pk,  # Pass the ID of the Mother instance
            'comment': 'some comment'
        }
        form = BanAdminForm(data=data)
        if form.is_valid():
            rendered_form = form.as_p()  # Render the form as HTML
            self.assertIn('<input type="hidden" name="mother" value="{}" id="id_mother">'.format(mother.pk),
                          rendered_form)

    def test_mother_id_from_url(self):
        mother = Mother.objects.create(name='name')
        request = RequestFactory().get(f'/admin/mothers/mother/add/?mother={mother.pk}')
        form = BanAdminForm(request=request)
        self.assertEqual(form.initial['mother'], str(mother.pk))
