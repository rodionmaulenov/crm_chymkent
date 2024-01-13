from django.db import models


class Stage(models.Model):
    class StageChoices(models.TextChoices):
        TRASH = 'Trash', 'trash'
        BAN = 'Ban', 'ban'
        PRIMARY = 'Primary', 'initial stage'
        FIRST_VISIT = 'First Visit', 'first visit'
        __empty__ = "(Unknown)"

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    stage = models.CharField(max_length=15, choices=StageChoices.choices, default=StageChoices.PRIMARY)
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_stage_display()
