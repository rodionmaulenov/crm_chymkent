# Generated by Django 4.2 on 2024-08-13 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0031_remove_doctoranswer_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctoranswer',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
