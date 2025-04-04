from ..models import HistorialClinico  # Asegúrate de que el modelo esté definido en models.py

def get_historias_clinicas():
    historias = HistorialClinico.objects.all()
    return historias


def get_historia_clinica(historias_clinica_id):
    return HistorialClinico.objects.get(pk=historias_clinica_id)

def crear_historia_clinica(data):
    historia = HistorialClinico(
        id_historial=data.get("id_historial"),
        paciente_id=data.get("paciente_id"),
        fecha=data.get("fecha"),
        ruta_contenido=data.get("ruta_contenido")
    )
    historia.save()
    return historia

def actualizar_historia_clinica(pk, new_data):
    historia = get_historia_clinica(pk)
    historia.paciente_id = new_data.get("paciente_id", historia.paciente_id)
    historia.fecha = new_data.get("fecha", historia.fecha)
    historia.ruta_contenido = new_data.get("ruta_contenido", historia.ruta_contenido)
    historia.save()

    return historia
