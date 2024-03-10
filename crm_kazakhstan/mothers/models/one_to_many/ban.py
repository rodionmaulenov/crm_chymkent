from django.db import models


class Ban(models.Model):
    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    banned = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.mother}.ban instance'

    class Meta:
        permissions = (
            ('ban_state', 'ban state'),
        )
