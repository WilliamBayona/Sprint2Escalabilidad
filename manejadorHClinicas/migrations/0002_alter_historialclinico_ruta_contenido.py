# Generated by Django 3.2.6 on 2025-04-02 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manejadorHClinicas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historialclinico',
            name='ruta_contenido',
            field=models.TextField(blank=True, null=True),
        ),
    ]
