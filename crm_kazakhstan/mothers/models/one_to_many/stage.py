from django.db import models


class Stage(models.Model):
    class StageChoices(models.TextChoices):
        TRASH = 'trash', 'trash'
        BAN = 'ban', 'ban'
        PRIMARY = 'primary', 'primary stage'
        FIRST_VISIT = 'first_visit', 'first visit'
        __empty__ = "-----"

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    stage = models.CharField(max_length=15, choices=StageChoices.choices, default=StageChoices.PRIMARY)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.get_stage_display()

