from django.db import models
from django.conf import settings

class EEGFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='eeg_files/')
    # Añadir campo para URL de Google Cloud Storage
    gcs_url = models.URLField(max_length=500, null=True, blank=True)
    recording_date = models.DateTimeField(null=True, blank=True)
    num_signals = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    sampling_rates = models.JSONField(default=dict)
    channel_names = models.JSONField(default=list)

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
            return self.file.url
        return None