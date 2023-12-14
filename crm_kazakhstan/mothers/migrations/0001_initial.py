# Generated by Django 3.2.23 on 2023-12-14 22:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mother',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('number', models.CharField(blank=True, max_length=100, null=True)),
                ('program', models.CharField(blank=True, max_length=100, null=True)),
                ('residence', models.CharField(blank=True, max_length=100, null=True)),
                ('height_and_weight', models.CharField(blank=True, max_length=100, null=True)),
                ('bad_habits', models.CharField(blank=True, max_length=100, null=True)),
                ('caesarean', models.CharField(blank=True, max_length=100, null=True)),
                ('children_age', models.CharField(blank=True, max_length=100, null=True)),
                ('age', models.CharField(blank=True, max_length=100, null=True)),
                ('citizenship', models.CharField(blank=True, max_length=100, null=True)),
                ('blood', models.CharField(blank=True, max_length=100, null=True)),
                ('maried', models.CharField(blank=True, max_length=100, null=True)),
                ('date_create', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'permissions': [('main_manager_condition_filter_option', 'Can filter mothers by inline on their questionnaire'), ('revoke_mothers', 'Can revoke mothers instance'), ('return_mothers', 'Can return mothers instance'), ('can_view_first_visit_mothers', 'Can view mothers with first visit stage')],
            },
        ),
        migrations.CreateModel(
            name='Messanger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('messanger', models.CharField(blank=True, choices=[('TEL', 'Telegram'), ('WTS', 'WhatsApp'), ('VIB', 'Viber')], max_length=3, null=True)),
                ('in_group', models.BooleanField(default=False)),
                ('date_add_in_group', models.DateField(auto_now_add=True)),
                ('mother', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother')),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(choices=[('WT', 'we talk'), ('CYC', 'cycle'), ('DAC', "doesn't answer the call"), ('WWW', 'wrote in WhatsApp and waiting'), ('WTW', 'wrote in Telegram and waiting'), ('NDE', "number doesn't exists"), ('PR', 'pregnant'), ('SIC', 'get sick'), ('HF', 'husband forbids'), ('ECR', 'examines children or relatives'), ('AN', 'another')], max_length=3)),
                ('reason', models.TextField(blank=True, null=True)),
                ('scheduled_date', models.DateField(blank=True, null=True)),
                ('scheduled_time', models.TimeField(blank=True, null=True)),
                ('mother', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('revoked', models.BooleanField(default=False)),
                ('mother', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mothers.mother')),
            ],
        ),
    ]
