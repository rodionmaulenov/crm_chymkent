# Generated by Django 4.2 on 2024-08-07 16:27

from django.db import migrations, models
import mothers.models.mother


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0025_alter_laboratory_analysis_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laboratoryfile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=mothers.models.mother.directory_path),
        ),
    ]
