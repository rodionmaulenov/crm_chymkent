from django.db import models


class Comment(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    banned = models.BooleanField(default=False)
