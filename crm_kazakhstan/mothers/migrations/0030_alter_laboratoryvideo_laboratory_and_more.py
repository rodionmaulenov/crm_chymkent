# Generated by Django 4.2 on 2024-08-12 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0029_alter_laboratoryvideo_ultrasound_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laboratoryvideo',
            name='laboratory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos_laboratory', to='mothers.laboratory'),
        ),
        migrations.AlterField(
            model_name='laboratoryvideo',
            name='ultrasound_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos_analysis', to='mothers.analysistype'),
        ),
    ]
