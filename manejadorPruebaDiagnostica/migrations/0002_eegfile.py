# Generated by Django 5.2 on 2025-05-03 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manejadorPruebaDiagnostica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EEGFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.CharField(blank=True, max_length=255, null=True)),
                ('gcs_url', models.URLField(blank=True, max_length=500, null=True)),
                ('recording_date', models.DateTimeField(blank=True, null=True)),
                ('num_signals', models.IntegerField(blank=True, null=True)),
                ('duration', models.FloatField(blank=True, null=True)),
                ('sampling_rates', models.JSONField(default=dict)),
                ('channel_names', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
