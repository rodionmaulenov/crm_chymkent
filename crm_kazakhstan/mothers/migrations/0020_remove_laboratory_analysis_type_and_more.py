# Generated by Django 4.0 on 2024-07-29 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0019_laboratory_analysis_type_delete_analysischoice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='laboratory',
            name='analysis_type',
        ),
        migrations.AddField(
            model_name='laboratory',
            name='analysis_types',
            field=models.ManyToManyField(related_name='laboratories', to='mothers.AnalysisType'),
        ),
        migrations.AlterField(
            model_name='laboratory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
