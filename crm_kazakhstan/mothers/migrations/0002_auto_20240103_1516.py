# Generated by Django 3.2.23 on 2024-01-03 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='stage',
            name='finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='stage',
            name='mother',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother'),
        ),
    ]
