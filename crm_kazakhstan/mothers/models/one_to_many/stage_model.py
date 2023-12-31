from django.db import models


class Stage(models.Model):
    class StageChoices(models.TextChoices):
        PRIMARY = 'Primary', 'undergoing medical tests'
        PARTICIPATION_IN_PROGRAM = 'Dipherelin', 'dipherelin'
        __empty__ = "(Unknown)"

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    stage = models.CharField(max_length=15, choices=StageChoices.choices, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.get_stage_display()
