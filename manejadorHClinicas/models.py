from django.db import models
from manejadorPacientes.models import Paciente

class HistorialClinico(models.Model):
    id_historial = models.AutoField(primary_key=True)
    paciente = models.OneToOneField("manejadorPacientes.Paciente", on_delete=models.CASCADE)  # Relación corregida
    fecha = models.DateField()
    ruta_contenido = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historial {self.id_historial}"


    


