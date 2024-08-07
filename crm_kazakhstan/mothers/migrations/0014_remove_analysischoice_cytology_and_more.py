# Generated by Django 4.0 on 2024-07-28 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0013_remove_laboratory_analysis_laboratory_analysis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysischoice',
            name='cytology',
        ),
        migrations.RemoveField(
            model_name='analysischoice',
            name='serology',
        ),
        migrations.RemoveField(
            model_name='laboratory',
            name='analysis',
        ),
        migrations.AddField(
            model_name='analysischoice',
            name='analysis_type',
            field=models.CharField(blank=True, choices=[('SEROLOGY', 'Serology'), ('CYTOLOGY', 'Cytology')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='analysischoice',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='analysis_files/'),
        ),
        migrations.AddField(
            model_name='laboratory',
            name='cytology',
            field=models.ForeignKey(blank=True, limit_choices_to={'analysis_type': 'CYTOLOGY'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cytology_tests', to='mothers.analysischoice'),
        ),
        migrations.AddField(
            model_name='laboratory',
            name='serology',
            field=models.ForeignKey(blank=True, limit_choices_to={'analysis_type': 'SEROLOGY'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='serology_tests', to='mothers.analysischoice'),
        ),
        migrations.AlterField(
            model_name='laboratory',
            name='mother',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='laboratories', to='mothers.mother'),
        ),
    ]
