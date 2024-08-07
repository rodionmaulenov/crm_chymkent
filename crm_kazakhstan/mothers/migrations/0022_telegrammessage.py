# Generated by Django 4.0 on 2024-08-01 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mothers', '0021_laboratoryfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.BigIntegerField()),
                ('chat_id', models.CharField(max_length=255)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('laboratory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mothers.laboratory')),
            ],
        ),
    ]
