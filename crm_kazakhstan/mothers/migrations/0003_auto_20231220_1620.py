# Generated by Django 3.2.23 on 2023-12-20 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0002_auto_20231220_1454'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MotherStep1',
        ),
        migrations.AlterField(
            model_name='stage',
            name='mother',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother'),
        ),
    ]
