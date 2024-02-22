from django.db import models


class Planned(models.Model):
    class PlannedChoices(models.TextChoices):
        TAKE_TESTS = 'Take tests', 'Analyzes in Shymkent'
        GO_THROUGH_THE_DOCTORS = 'Doctors', 'Go for doctors'
        ADDITIONAL_VERIFYING = 'Verifying', 'Extra treatment'
        __empty__ = "(Unknown)"

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    plan = models.CharField(max_length=15, choices=PlannedChoices.choices, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return 'The planned events'
