from django.db import models

class TipoExamen(models.TextChoices):
    PRUEBA_EEG = 'EEG', 'pruebaEEG'
    PRUEBA_MRI = 'MRI', 'pruebaMRI'
    PRUEBA_MIRNA = 'MiRNA', 'pruebaMiRNA'