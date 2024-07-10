from django.test import TestCase
from mothers.models import Mother
from mothers.tasks import delete_weekend_objects
from freezegun import freeze_time


class DeleteWeekendObjectsTestCase(TestCase):

    @freeze_time("2024-07-01 23:00:00")
    def create_previous_week_monday_objs(self):
        mother = Mother.objects.create(name="Mother1", age=None)
        return mother

    @freeze_time("2024-07-02 23:00:00")
    def create_previous_week_tuesday_objs(self):
        mother = Mother.objects.create(name="Mother2", residence=None)
        return mother

    @freeze_time("2024-07-03 23:00:00")
    def create_previous_week_wednesday_objs(self):
        mother = Mother.objects.create(name="Mother3", height=None)
        return mother

    @freeze_time("2024-07-04 23:00:00")
    def create_previous_week_thursday_objs(self):
        mother = Mother.objects.create(name="Mother4", weight=None)
        return mother

    @freeze_time("2024-07-05 23:59:59")
    def create_previous_week_friday_objs(self):
        mother = Mother.objects.create(name="Mother5", caesarean=None)
        return mother

    @freeze_time("2024-07-06 23:00:00")
    def create_previous_week_saturday_objs(self):
        mother = Mother.objects.create(name="Mother6", children=None)
        return mother

    @freeze_time("2024-07-07 23:00:00")
    def create_previous_week_sunday_objs(self):
        mother = Mother.objects.create(name="Mother6", children=None)
        return mother

    @freeze_time("2024-07-01 23:00:00")
    def create_previous_week_monday_objs_without_null_fields(self):
        # Create instances without null fields in the previous week
        mother = Mother.objects.create(name="Mother7", age=30, residence="New York", height="170", weight="65", caesarean=1,
                              children=2, blood=Mother.BloodChoice.SECOND_POSITIVE, maried=True)
        return mother

    @freeze_time("2024-07-03 23:00:00")
    def create_previous_week_wednesday_objs_without_null_fields(self):
        mother = Mother.objects.create(name="Mother8", age=30, residence="New York", height="170", weight="65", caesarean=1,
                              children=2, blood=Mother.BloodChoice.SECOND_POSITIVE, maried=True)
        return mother

    @freeze_time("2024-07-08 10:00:00")
    def instances_with_null_fields_outside_the_previous_week1(self):
        mother = Mother.objects.create(name="Mother9", age=None)
        return mother

    @freeze_time("2024-07-08 11:00:00")
    def instances_with_null_fields_outside_the_previous_week2(self):
        mother = Mother.objects.create(name="Mother10", residence=None)
        return mother

    @freeze_time("2024-07-13 00:00:00")
    def test_delete_objs_from_previous_monday_to_friday_inclusive(self):
        # Create instances
        monday = self.create_previous_week_monday_objs()
        tuesday = self.create_previous_week_tuesday_objs()
        wednesday = self.create_previous_week_wednesday_objs()
        thursday = self.create_previous_week_thursday_objs()
        friday = self.create_previous_week_friday_objs()
        saturday = self.create_previous_week_saturday_objs()
        sunday = self.create_previous_week_sunday_objs()

        self.create_previous_week_monday_objs_without_null_fields()
        self.create_previous_week_wednesday_objs_without_null_fields()
        self.instances_with_null_fields_outside_the_previous_week1()
        self.instances_with_null_fields_outside_the_previous_week2()

        # Run the task
        delete_weekend_objects()

        # Check that the instances with null fields created on weekdays have been deleted
        self.assertTrue(Mother.objects.filter(id=monday.id).exists())
        self.assertTrue(Mother.objects.filter(id=tuesday.id).exists())
        self.assertTrue(Mother.objects.filter(id=wednesday.id).exists())
        self.assertTrue(Mother.objects.filter(id=thursday.id).exists())
        self.assertTrue(Mother.objects.filter(id=friday.id).exists())

        # Check that the instances created on the weekend and those without null fields are still there
        self.assertFalse(Mother.objects.filter(id=saturday.id).exists())
        self.assertFalse(Mother.objects.filter(id=sunday.id).exists())

        # Check that the instances created on weekdays without null fields are still there
        self.assertTrue(Mother.objects.filter(name="Mother7").exists())
        self.assertTrue(Mother.objects.filter(name="Mother8").exists())

        # Check that the instances created outside the previous week are still there
        self.assertTrue(Mother.objects.filter(name="Mother9").exists())
        self.assertTrue(Mother.objects.filter(name="Mother10").exists())