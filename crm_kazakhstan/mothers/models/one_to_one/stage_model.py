from django.db import models


class Stage(models.Model):
    class StageChoices(models.TextChoices):
        PRIMARY = 'Primary', 'get tested'
        PARTICIPATION_IN_PROGRAM = 'Dipherelin', 'dipherelin'
        __empty__ = "(Unknown)"

    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    stage = models.CharField(max_length=15, choices=StageChoices.choices, blank=True, null=True)

    def __str__(self):
        return self.get_stage_display()
