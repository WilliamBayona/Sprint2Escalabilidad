from django.db import models

# Create your models here

class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    edad = models.IntegerField()
    genero = models.CharField(max_length=50)
    tipo_sangre = models.CharField(max_length=5)
    alergias = models.TextField(blank=True, null=True)
    condiciones_medicas = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre