# Generated by Django 3.2.23 on 2024-01-29 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0004_alter_condition_condition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condition',
            name='condition',
            field=models.CharField(blank=True, choices=[(None, '__empty__'), ('created', 'recently created'), ('no baby', 'has not baby'), ('WWW', 'wrote WhatsApp, waiting the answer')], default='__empty__', max_length=10, null=True),
        ),
    ]
