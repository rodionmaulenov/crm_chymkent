# Generated by Django 3.2.25 on 2024-04-11 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0002_banproxy'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentProxy',
            fields=[
            ],
            options={
                'verbose_name': 'document',
                'verbose_name_plural': 'documents',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mothers.mother',),
        ),
    ]
