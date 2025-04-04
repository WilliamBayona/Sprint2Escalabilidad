from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from .logic.logic_historiasClinicas import get_historias_clinicas, get_historia_clinica, crear_historia_clinica, actualizar_historia_clinica
from django.views.decorators.csrf import csrf_exempt  
from .models import HistorialClinico
import json

def lista_historias_clinicas(request):
    historias = HistorialClinico.objects.all()
    data = {"historias_clinicas": list(historias.values())}
    return JsonResponse(data)

def historias_clinicas_view(request):
    if request.method == 'GET':
        historias = get_historias_clinicas()
        historias_dto = serializers.serialize('json', historias)
        return HttpResponse(historias_dto, content_type='application/json')

@csrf_exempt
def historias_clinicas_view(request):
    if request.method == 'GET':
        historia_clinica_id = request.GET.get("historia_clinica_id", None)

        if historia_clinica_id:
            historia_clinica_dto = get_historia_clinica(historia_clinica_id)
            historia_clinica = serializers.serialize('json', [historia_clinica_dto,])
            return HttpResponse(historia_clinica, 'application/json')
        else:
            historias_clinicas_dto = get_historias_clinicas()
            historias_clinicas = serializers.serialize('json', [historias_clinicas_dto,])
            return HttpResponse(historias_clinicas, 'application/json')  

    if request.method == 'POST':
        historia_clinica_dto = crear_historia_clinica(json.loads(request.body))
        historia_clinica_json = serializers.serialize('json', [historia_clinica_dto,])
        return HttpResponse(historia_clinica, 'application/json')

@csrf_exempt
def historia_clinica_view(request, pk):
    if request.method == 'GET':
        historia_clinica = get_historia_clinica(pk)
        historia_clinica_dto = serializers.serialize('json', [historia_clinica]) 
        return JsonResponse(historia_clinica_dto, safe=False)
    
    if request.method == 'PUT':
        historia_dto = actualizar_historia_clinica(pk, json.loads(request.body))
        historia = serializers.serialize('json', [historia_dto])
        return HttpResponse(historia, 'application/json')