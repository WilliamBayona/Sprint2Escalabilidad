from django.http import JsonResponse
from .models import Paciente
from django.http import HttpResponse
from django.core import serializers
from .logic.logic_pacientes import get_pacientes, get_paciente, crear_paciente, actualizar_paciente
from django.views.decorators.csrf import csrf_exempt
import json


def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    data = {"pacientes": list(pacientes.values())}
    return JsonResponse(data)

def pacientes_view(request):
    if request.method == 'GET':
        pacientes = get_pacientes()
        pacientes_dto = serializers.serialize('json', pacientes)
        return HttpResponse(pacientes_dto, content_type='application/json')
    

@csrf_exempt
def pacientes_view(request):
    if request.method == 'GET':
        paciente_id = request.GET.get("paciente_id", None)

        if paciente_id:
            paciente_dto = get_paciente(paciente_id)
            paciente = serializers.serialize('json', [paciente_dto,])
            return HttpResponse(paciente, 'application/json')
        else:
            pacientes_dto = get_pacientes()
            pacientes = serializers.serialize('json', [pacientes_dto,])
            return HttpResponse(pacientes, 'application/json')  

    if request.method == 'POST':
        paciente_dto = crear_paciente(json.loads(request.body))
        paciente_json = serializers.serialize('json', [paciente_dto,])
        return HttpResponse(paciente, 'application/json')

@csrf_exempt
def paciente_view(request, pk):
    if request.method == 'GET':
        paciente = get_paciente(pk)
        paciente_dto = serializers.serialize('json', [paciente])  # Se serializa como JSON
        return JsonResponse(paciente_dto, safe=False)
    if request.method == 'PUT':
        paciente_dto = actualizar_paciente(pk, json.loads(request.body))
        paciente = serializers.serialize('json', [paciente_dto])
        return HttpResponse(paciente, 'application/json')