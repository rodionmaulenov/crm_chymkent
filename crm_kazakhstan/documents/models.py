from django.db import models

from mothers.models import Mother


class Document(models.Model):
    class DocumentChoices(models.TextChoices):
        MAIN_DOCS = 'main_docs', 'main documents'
        ACQUIRE_DOCS = 'acquire_docs', 'acquire documents'
        ADDITIONAL_DOCS = 'additional_docs', 'additional documents'
        __empty__ = "-----"

    class NameChoices(models.TextChoices):
        PASSPORT = 'passport', 'passport'
        __empty__ = "-----"

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    document_kind = models.CharField(max_length=15, choices=DocumentChoices.choices, null=True, blank=True)
    name = models.CharField(max_length=255, choices=NameChoices.choices, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField()
