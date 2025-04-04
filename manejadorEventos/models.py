from django.db import models
from manejadorPacientes.models import Paciente

class EventoMedico(models.Model):
    fecha = models.DateField()
    motivo = models.TextField()
    paciente = models.ForeignKey("manejadorPacientes.Paciente", on_delete=models.CASCADE, related_name="eventos_medicos")

    def __str__(self):
        return f"Evento  {self.paciente}"
