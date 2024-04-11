# Generated by Django 3.2.25 on 2024-04-11 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_documentproxy'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DocumentProxy',
        ),
        migrations.AlterField(
            model_name='document',
            name='title',
            field=models.CharField(blank=True, choices=[(None, '-----'), ('main_docs', 'main documents'), ('acquire_docs', 'acquire documents'), ('additional_docs', 'additional documents')], max_length=255, null=True),
        ),
    ]
