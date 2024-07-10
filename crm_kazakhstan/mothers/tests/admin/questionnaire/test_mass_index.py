from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.utils.html import format_html

from mothers.admin import QuestionnaireAdmin
from mothers.models import Mother

User = get_user_model()


class MassIndexTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_instance = QuestionnaireAdmin(Mother, admin.site)

        # Create test user
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create test Mother instances
        self.mother_normal = Mother.objects.create(name="Normal", weight=70, height=175)  # BMI = 22.9
        self.mother_underweight = Mother.objects.create(name="Underweight", weight=45, height=175)  # BMI = 14.7
        self.mother_overweight = Mother.objects.create(name="Overweight", weight=85, height=175)  # BMI = 27.8
        self.mother_obesity1 = Mother.objects.create(name="Obesity1", weight=95, height=175)  # BMI = 31.0
        self.mother_obesity2 = Mother.objects.create(name="Obesity2", weight=110, height=175)  # BMI = 35.9
        self.mother_obesity3 = Mother.objects.create(name="Obesity3", weight=130, height=175)  # BMI = 42.4

    def test_mass_index_normal(self):
        result = self.admin_instance.mass_index(self.mother_normal)
        self.assertEqual(result, format_html("22.8/Normal weight (18.5-24.9) - Normal"))

    def test_mass_index_underweight(self):
        result = self.admin_instance.mass_index(self.mother_underweight)
        self.assertEqual(result,
                         format_html("<span style='color: red;'>14.6/Underweight (less than 18.5) - Low</span>"))

    def test_mass_index_overweight(self):
        result = self.admin_instance.mass_index(self.mother_overweight)
        self.assertEqual(result, format_html(
            "<span style='color: red;'>27.7/Overweight (pre-obesity) (25.0-29.9) - Increased</span>"))

    def test_mass_index_obesity1(self):
        result = self.admin_instance.mass_index(self.mother_obesity1)
        self.assertEqual(result,
                         format_html("<span style='color: red;'>31.0/Obesity Class I (30.0-34.9) - High</span>"))

    def test_mass_index_obesity2(self):
        result = self.admin_instance.mass_index(self.mother_obesity2)
        self.assertEqual(result,
                         format_html("<span style='color: red;'>35.9/Obesity Class II (35.0-39.9) - Very High</span>"))

    def test_mass_index_obesity3(self):
        result = self.admin_instance.mass_index(self.mother_obesity3)
        self.assertEqual(result, format_html(
            "<span style='color: red;'>42.4/Obesity Class III (40.0 and above) - Extremely High</span>"))
