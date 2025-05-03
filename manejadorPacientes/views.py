from django.http import JsonResponse
from django.shortcuts import render
from .models import Paciente
from django.http import HttpResponse
from django.core import serializers
from .logic.logic_pacientes import get_pacientes, get_paciente, crear_paciente, actualizar_paciente
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.urls import path
import proyecto.auth0backend as auth0backend



def getRole(request):
    user = request.user
    auth0user = user.social_auth.filter(provider="auth0")[0]
    accessToken = auth0user.extra_data['access_token']
    
    # Use string literals directly for URLs
    url = "https://dev-y3lnnddg1z815lbo.us.auth0.com/userinfo"  
    headers = {'authorization': f'Bearer {accessToken}'}
    
    resp = requests.get(url, headers=headers)
    userinfo = resp.json()
    
    # Use string literals for accessing the role key
    role = userinfo["https://dev-y3lnnddg1z815lbo.us.auth0.com/role"]  
    return role

def lista_pacientes(request):
    # Si se solicita JSON (por ejemplo, desde una API)
    if request.headers.get('Accept') == 'application/json':
        pacientes = Paciente.objects.all()
        data = {"pacientes": list(pacientes.values())}
        return JsonResponse(data)
    
    # Para solicitudes de navegador (HTML)
    pacientes = Paciente.objects.all()
    return render(request, 'lista_pacientes.html', {'pacientes': pacientes})

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
        
        # Si se solicita JSON (por ejemplo, desde una API)
        if request.headers.get('Accept') == 'application/json':
            paciente_dto = serializers.serialize('json', [paciente])
            return JsonResponse(paciente_dto, safe=False)
        
        # Para solicitudes de navegador (HTML)
        return render(request, 'detalle_paciente.html', {'paciente': paciente})
        
    if request.method == 'PUT':
        paciente_dto = actualizar_paciente(pk, json.loads(request.body))
        paciente = serializers.serialize('json', [paciente_dto])
        return HttpResponse(paciente, content_type='application/json')