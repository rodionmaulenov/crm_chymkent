from django.db import models


class Planned(models.Model):
    class PlannedChoices(models.TextChoices):
        TAKE_TESTS = 'Tests', 'Analyzes in Shymkent'
        GO_THROUGH_THE_DOCTORS = 'Doctors', 'Go for doctors'
        ADDITIONAL_VERIFYING = 'Verifying', 'Extra treatment'
        __empty__ = "(Unknown)"

    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    plan = models.CharField(max_length=15, choices=PlannedChoices.choices)
    note = models.CharField(max_length=255, blank=True, null=True)