# Generated by Django 3.2.23 on 2023-12-25 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0019_alter_comment_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condition',
            name='mother',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother'),
        ),
    ]
