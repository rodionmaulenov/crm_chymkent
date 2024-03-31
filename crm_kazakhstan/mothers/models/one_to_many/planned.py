from django.db import models


class Planned(models.Model):
    class PlannedChoices(models.TextChoices):
        FIRST_TEST = 'laboratory', 'laboratory is planned'
        __empty__ = "-----"

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    plan = models.CharField(max_length=15, choices=PlannedChoices.choices)
    note = models.CharField(max_length=255, blank=True, null=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    created = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.get_plan_display()
