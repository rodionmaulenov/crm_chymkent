# Generated by Django 4.2 on 2024-08-11 19:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mothers.models.mother


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0027_laboratoryvideo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='laboratoryvideo',
            name='video',
        ),
        migrations.AddField(
            model_name='laboratoryvideo',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='laboratoryvideo',
            name='ultrasound_file',
            field=models.FileField(blank=True, null=True, upload_to=mothers.models.mother.directory_path_video),
        ),
        migrations.AddField(
            model_name='laboratoryvideo',
            name='ultrasound_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='video_or_file_ultrasound', to='mothers.analysistype'),
        ),
        migrations.AddField(
            model_name='laboratoryvideo',
            name='ultrasound_video',
            field=models.FileField(blank=True, null=True, upload_to=mothers.models.mother.directory_path_video),
        ),
        migrations.AlterField(
            model_name='analysistype',
            name='name',
            field=models.CharField(choices=[('SEROLOGY', 'Serology'), ('CYTOLOGY', 'Cytology'), ('ULTRASOUND', 'Ultrasound')], max_length=20, unique=True),
        ),
    ]