from ..models import EventoMedico

def get_eventos():
    eventos = EventoMedico.objects.all()
    return eventos

def get_evento(evento_id):
    return EventoMedico.objects.get(pk=evento_id)

def crear_evento(data):
    evento = EventoMedico(
        historia_clinica_id=data.get("historia_clinica_id"),
        motivo=data.get("motivo"),
        fecha=data.get("fecha")
    )
    evento.save()
    return evento

def actualizar_evento(pk, new_data):
    evento = get_evento(pk)
    evento.historia_clinica_id = new_data.get("historia_clinica_id", evento.historia_clinica_id)
    evento.motivo = new_data.get("motivo", evento.motivo)
    evento.fecha = new_data.get("fecha", evento.fecha)
    evento.save() 
    
    return evento

