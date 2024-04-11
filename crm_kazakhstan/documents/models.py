from django.db import models

from mothers.models import Mother


class Document(models.Model):
    class DocumentTitleBase(models.TextChoices):
        PASSPORT = 'passport', 'passport'

    class DocumentChoices(models.TextChoices):
        MAIN_DOCS = 'main_docs', 'main documents'
        ACQUIRE_DOCS = 'acquire_docs', 'acquire documents'
        ADDITIONAL_DOCS = 'additional_docs', 'additional documents'
        __empty__ = "-----"

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, choices=DocumentChoices.choices, blank=True, null=True)
    document_kind = models.CharField(max_length=15, choices=DocumentChoices.choices, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField()


class DocumentProxy(Mother):
    class Meta:
        app_label = 'mothers'
        verbose_name = 'document'
        verbose_name_plural = 'documents'
        proxy = True
