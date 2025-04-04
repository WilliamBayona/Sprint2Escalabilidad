from django.db import models
from django.conf import settings

class EEGFile(models.Model):
    id = models.AutoField(primary_key=True)
    
    # Cambiamos esto para soportar tanto archivos locales como en GCS
    file = models.CharField(max_length=255, blank=True, null=True)
    
    # Campo para la URL pública de GCS (solo se usa si estamos en GCS)
    gcs_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Metadatos del EEG
    recording_date = models.DateTimeField(null=True, blank=True)
    num_signals = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    sampling_rates = models.JSONField(default=dict)
    channel_names = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EEG File {self.id}"
    
    @property
    def url(self):
        """
        Retorna la URL para acceder al archivo (compatible con ambos modos de almacenamiento)
        """
        if getattr(settings, 'USE_GCS', False) and self.gcs_url:
            return self.gcs_url
        elif self.file:
            return f"{settings.MEDIA_URL}{self.file}"
        return None

from manejadorEEGFile.models import EEGFile
from manejadorTipoExamen.models import TipoExamen

class PruebaDiagnostica(models.Model):
    tipo_de_prueba = models.CharField(
        max_length=10,
        choices=TipoExamen.choices,
        default=TipoExamen.PRUEBA_EEG
    )
    fecha = models.DateTimeField()
    resultados = models.TextField(null=True, blank=True)
    comentarios = models.TextField(null=True, blank=True)
    presencia_anomalia = models.BooleanField(default=False)
    tipo_anomalia = models.CharField(max_length=255, null=True, blank=True)
    presencia_lesion = models.BooleanField(default=False)
    tipo_lesion = models.CharField(max_length=255, null=True, blank=True)
    presencia_sobreexpresion = models.BooleanField(default=False)
    
    eeg_file = models.OneToOneField('manejadorEEGFile.EEGFile', on_delete=models.CASCADE, null=True, blank=True)
    historial_clinico = models.ForeignKey('manejadorHClinicas.HistorialClinico', on_delete=models.CASCADE)
    paciente = models.ManyToManyField('manejadorPacientes.Paciente')
    def __str__(self):
        return f"{self.get_tipo_de_prueba_display()} - {self.fecha}"