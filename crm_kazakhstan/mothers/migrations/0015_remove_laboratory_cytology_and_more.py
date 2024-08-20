# Generated by Django 4.0 on 2024-07-29 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0014_remove_analysischoice_cytology_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='laboratory',
            name='cytology',
        ),
        migrations.RemoveField(
            model_name='laboratory',
            name='serology',
        ),
        migrations.AddField(
            model_name='laboratory',
            name='analysis',
            field=models.ManyToManyField(related_name='laboratories', to='mothers.AnalysisChoice'),
        ),
        migrations.AlterField(
            model_name='analysischoice',
            name='analysis_type',
            field=models.CharField(choices=[('SEROLOGY', 'Serology'), ('CYTOLOGY', 'Cytology')], max_length=20),
        ),
    ]