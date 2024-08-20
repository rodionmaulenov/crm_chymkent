# Generated by Django 4.0 on 2024-07-29 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0020_remove_laboratory_analysis_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaboratoryFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='laboratory_files/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('analysis_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files_analysis', to='mothers.analysistype')),
                ('laboratory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files_laboratory', to='mothers.laboratory')),
            ],
        ),
    ]