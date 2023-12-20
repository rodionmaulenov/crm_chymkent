from django.db import models


class Comment(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    description = models.TextField()
    revoked = models.BooleanField(default=False)
