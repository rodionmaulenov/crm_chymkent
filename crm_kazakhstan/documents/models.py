from django.db import models

from mothers.models import Mother


class Document(models.Model):
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    document = models.FileField(blank=True, null=True)
