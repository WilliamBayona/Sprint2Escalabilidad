from ..models import Paciente  # Asegúrate de que el modelo esté definido en models.py

def get_pacientes():
    pacientes = Paciente.objects.all()
    return pacientes

def get_paciente(paciente_id):
    return Paciente.objects.get(pk=paciente_id)

def crear_paciente(data):
    paciente = Paciente(
        paciente_id=data.get("paciente_id"),
        nombre=data.get("nombre"),
        id_historial=data.get("id_historial"),
        edad=data.get("edad"),
        genero=data.get("genero"),
        tipo_sangre=data.get("tipo_sangre"),
        alergias=data.get("alergias"),
        condiciones_medicas=data.get("condiciones_medicas")
    )
    paciente.save()
    return paciente

def actualizar_paciente(pk, new_data):
    paciente = get_paciente(pk) 
    
    paciente.paciente_id = new_data.get("paciente_id", paciente.paciente_id)
    paciente.nombre = new_data.get("nombre", paciente.nombre)
    paciente.id_historial = new_data.get("id_historial", paciente.id_historial)
    paciente.edad = new_data.get("edad", paciente.edad)
    paciente.genero = new_data.get("genero", paciente.genero)
    paciente.tipo_sangre = new_data.get("tipo_sangre", paciente.tipo_sangre)
    paciente.alergias = new_data.get("alergias", paciente.alergias)
    paciente.condiciones_medicas = new_data.get("condiciones_medicas", paciente.condiciones_medicas)
    
    paciente.save()
    return paciente

