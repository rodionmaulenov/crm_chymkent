# Generated by Django 3.2.25 on 2024-07-09 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gmail_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='country',
            field=models.CharField(blank=True, choices=[('UZBEKISTAN', 'Uzbekistan'), ('KYRGYZSTAN', 'Kyrgyzstan')], max_length=30, null=True),
        ),
    ]