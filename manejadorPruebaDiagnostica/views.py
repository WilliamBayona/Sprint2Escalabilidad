from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  # Añade esta importación
import mne
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import PruebaDiagnostica
from .logic.logic_PruebaDiagnostica import (
    get_pruebas_diagnosticas, 
    get_prueba_diagnostica, 
    crear_prueba_diagnostica, 
    actualizar_prueba_diagnostica,
    subir_archivo_eeg
)
import tempfile
import json
from mne.io import read_raw_edf
from .models import EEGFile as EEGFileModel
import os
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64
from django.template.loader import render_to_string
from mne.viz import plot_raw
matplotlib.use('Agg')  # Use non-interactive backend
from google.cloud import storage
import hashlib
from django.core.cache import cache

def lista_pruebas_diagnosticas(request):
    pruebas = get_pruebas_diagnosticas()
    data = {"pruebas_diagnosticas": list(pruebas.values())}
    return JsonResponse(data)

@csrf_exempt
def pruebas_diagnosticas_view(request):
    if request.method == 'GET':
        prueba_id = request.GET.get("prueba_id", None)
        if (prueba_id):
            prueba_dto = get_prueba_diagnostica(prueba_id)
            prueba = serializers.serialize('json', [prueba_dto])
            return HttpResponse(prueba, content_type='application/json')
        else:
            pruebas_dto = get_pruebas_diagnosticas()
            pruebas = serializers.serialize('json', pruebas_dto)
            return HttpResponse(pruebas, content_type='application/json')
    
    if request.method == 'POST':
        prueba_dto = crear_prueba_diagnostica(json.loads(request.body))
        prueba_json = serializers.serialize('json', [prueba_dto])
        return HttpResponse(prueba_json, content_type='application/json')

@csrf_exempt
def prueba_diagnostica_view(request, pk):
    if request.method == 'GET':
        prueba = get_prueba_diagnostica(pk)
        prueba_dto = serializers.serialize('json', [prueba])
        return JsonResponse(prueba_dto, safe=False)
    
    if request.method == 'PUT':
        prueba_dto = actualizar_prueba_diagnostica(pk, json.loads(request.body))
        prueba = serializers.serialize('json', [prueba_dto])
        return HttpResponse(prueba, content_type='application/json')

@csrf_exempt
def subir_eeg_view(request, pk):
    if request.method == 'POST':
        print("REQUEST.FILES:", request.FILES)

        if 'archivo' not in request.FILES:
            print("No se encontró 'archivo' en REQUEST.FILES")
            return JsonResponse({"error": "No se envió ningún archivo."}, status=400)

        archivo = request.FILES['archivo']
        print(f"Archivo recibido: {archivo.name} ({archivo.content_type})")

        try:
            eeg_file, error = subir_archivo_eeg(pk, archivo)

            if error:
                print(f"Error en subir_archivo_eeg: {error}")
                return JsonResponse({"error": error}, status=400)

            eeg_json = serializers.serialize('json', [eeg_file])
            print("Archivo EEG procesado correctamente.")
            return HttpResponse(eeg_json, content_type='application/json')

        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

@csrf_exempt
def upload_eeg(request, prueba_id):
    if request.method == 'POST':
        try:
            prueba = PruebaDiagnostica.objects.get(id=prueba_id)
            if prueba.tipo_de_prueba != 'EEG':
                return JsonResponse({"error": "Solo las pruebas EEG pueden tener archivos EDF."}, status=400)

            if 'archivo' not in request.FILES:
                return JsonResponse({"error": "No se envió ningún archivo."}, status=400)

            archivo = request.FILES['archivo']
            print(f"Archivo recibido: {archivo.name} ({archivo.content_type})")  # Depuración

            eeg_file = EEGFileModel(file=archivo)

            # Guardar el archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as temp_file:
                temp_file.write(archivo.read())
                temp_file_path = temp_file.name  # Ruta del archivo temporal

            try:
                # Cargar el EDF desde la ruta
                raw = mne.io.read_raw_edf(temp_file_path, preload=True)
                print("Archivo EDF cargado correctamente")

                # Extraer metadatos
                eeg_file.recording_date = raw.info['meas_date']
                eeg_file.num_signals = len(raw.ch_names)
                eeg_file.duration = raw.times[-1]  # Último valor de tiempo
                eeg_file.channel_names = raw.ch_names
                eeg_file.sampling_rates = {ch: raw.info['sfreq'] for ch in raw.ch_names}

                eeg_file.save()

                # Asociar el archivo EEG con la prueba diagnóstica
                prueba.eeg_file = eeg_file
                prueba.save()

                eeg_json = serializers.serialize('json', [eeg_file])
                return HttpResponse(eeg_json, content_type='application/json')

            except Exception as e:
                print(f"Error procesando el archivo EDF: {str(e)}")
                return JsonResponse({"error": f"Error procesando el archivo EDF: {str(e)}"}, status=500)

            finally:
                os.remove(temp_file_path)  # Eliminar archivo temporal después de usarlo

        except PruebaDiagnostica.DoesNotExist:
            return JsonResponse({"error": "Prueba diagnóstica no encontrada."}, status=404)

@csrf_exempt
def visualizar_eeg_view(request, pk):
    """
    View para visualizar datos EEG desde un archivo (GCS o local)
    """
    try:
        prueba = PruebaDiagnostica.objects.get(id=pk)
        
        if prueba.tipo_de_prueba != 'EEG' or not prueba.eeg_file:
            return JsonResponse({"error": "No hay archivo EEG disponible para esta prueba."}, status=400)
        
        # Generar una clave única para esta prueba/visualización
        cache_key = f"eeg_visual_{pk}_{prueba.eeg_file.id}"
        
        # Intentar obtener de caché primero
        cached_result = cache.get(cache_key)
        if cached_result:
            print("Usando visualización en caché")
            return render(request, 'visualizacion_eeg.html', cached_result)
            
        # Si no está en caché, continuar con el procesamiento normal
        temp_file_path = None
        
        try:
            # Crear un archivo temporal para trabajar
            with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as temp_file:
                temp_file_path = temp_file.name
            
            # Determinar fuente del archivo según configuración
            use_gcs = getattr(settings, 'USE_GCS', False)
            
            if use_gcs and prueba.eeg_file.gcs_url:
                # Descargar desde Google Cloud Storage usando credenciales explícitas
                try:
                    from google.cloud import storage
                    from google.oauth2 import service_account
                    
                    # Usar la ruta configurada en settings.py
                    credentials_file = settings.GS_CREDENTIALS_FILE
                    
                    if not os.path.exists(credentials_file):
                        return JsonResponse({"error": f"El archivo de credenciales no existe: {credentials_file}"}, status=500)
                    
                    print(f"Cargando credenciales desde: {credentials_file}")
                    # Crear credenciales de manera explícita
                    credentials = service_account.Credentials.from_service_account_file(credentials_file)
                    
                    # Crear cliente con las credenciales
                    client = storage.Client(
                        project=settings.GS_PROJECT_ID,
                        credentials=credentials
                    )
                    
                    # Obtener referencia al bucket y blob
                    bucket = client.bucket(settings.GS_BUCKET_NAME)
                    # file_name debe ser una cadena, no un objeto FieldFile
                    if hasattr(prueba.eeg_file, 'file'):
                        if isinstance(prueba.eeg_file.file, str):
                            file_name = prueba.eeg_file.file  # Ya es una cadena
                        else:
                            file_name = prueba.eeg_file.file.name  # Obtener el nombre como cadena
                    else:
                        return JsonResponse({"error": "No se pudo determinar el nombre del archivo"}, status=400)

                    print(f"Intentando acceder al blob: {file_name}")
                    blob = bucket.blob(file_name)
                    
                    # Descargar al archivo temporal
                    blob.download_to_filename(temp_file_path)
                    print(f"Archivo descargado desde GCS a {temp_file_path}")
                    
                except Exception as e:
                    import traceback
                    print(f"Error descargando desde GCS: {e}")
                    traceback.print_exc()
                    return JsonResponse({"error": f"Error al acceder al archivo en Google Cloud: {str(e)}"}, status=500)
            else:
                # Obtener desde almacenamiento local
                try:
                    file_path = os.path.join(settings.MEDIA_ROOT, prueba.eeg_file.file)
                    if not os.path.exists(file_path):
                        return JsonResponse({"error": f"Archivo no encontrado: {file_path}"}, status=404)
                    
                    # Copiar al archivo temporal
                    import shutil
                    shutil.copy2(file_path, temp_file_path)
                    print(f"Archivo copiado desde local: {file_path} -> {temp_file_path}")
                    
                except Exception as e:
                    print(f"Error accediendo al archivo local: {e}")
                    return JsonResponse({"error": f"Error al acceder al archivo local: {str(e)}"}, status=500)
            
            # Proceso de visualización con MNE
            raw = mne.io.read_raw_edf(temp_file_path, preload=True)
            
            # Seleccionar canales y segmento para visualizar
            channels_to_plot = raw.ch_names[:8]  # Primeros 8 canales
            start_idx = 0
            end_idx = int(10 * raw.info['sfreq'])  # 10 segundos de datos
            
            data, times = raw.get_data(picks=channels_to_plot, 
                                      start=start_idx, 
                                      stop=end_idx, 
                                      return_times=True)
            
            # Crear figura
            fig, ax = plt.subplots(len(channels_to_plot), 1, figsize=(12, 8), sharex=True)
            
            # Graficar cada canal
            for i, ch_name in enumerate(channels_to_plot):
                if len(channels_to_plot) > 1:
                    ax[i].plot(times, data[i])
                    ax[i].set_ylabel(ch_name)
                else:
                    ax.plot(times, data[i])
                    ax.set_ylabel(ch_name)
            
            # Configurar etiquetas comunes
            if len(channels_to_plot) > 1:
                ax[-1].set_xlabel('Tiempo (s)')
                fig.suptitle(f'EEG de prueba {pk}')
            else:
                ax.set_xlabel('Tiempo (s)')
                ax.set_title(f'EEG de prueba {pk}')
            
            fig.tight_layout()
            
            # Guardar figura en buffer y convertir a base64
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            
            # Preparar contexto para la plantilla
            context = {
                'prueba': prueba,
                'eeg_image': image_base64,
                'recording_date': prueba.eeg_file.recording_date,
                'num_signals': prueba.eeg_file.num_signals,
                'duration': prueba.eeg_file.duration,
                'channel_names': prueba.eeg_file.channel_names[:10],
                'file_url': prueba.eeg_file.url,  # URL del archivo (GCS o local)
            }
            
            # Guardar en caché por 10 minutos
            cache.set(cache_key, context, 600)
            
            return render(request, 'visualizacion_eeg.html', context)
            
        finally:
            # Limpieza: eliminar archivo temporal
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Error al procesar la solicitud: {str(e)}"}, status=500)
        
    except PruebaDiagnostica.DoesNotExist:
        return JsonResponse({"error": "Prueba diagnóstica no encontrada."}, status=404)

def upload_eeg_file(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        eeg_file = EEGFile(
            # otros campos...
            archivo=request.FILES['archivo']
        )
        eeg_file.save()
        # El archivo se cargará automáticamente al bucket de GCS
        return redirect('success_url')
    return render(request, 'upload_form.html')

# Añadir esta vista para depuración

def check_gcs_config(request):
    """
    Vista de depuración para verificar la configuración de GCS
    """
    from django.http import HttpResponse
    import json
    
    result = {
        'USE_GCS': getattr(settings, 'USE_GCS', False),
        'GS_BUCKET_NAME': getattr(settings, 'GS_BUCKET_NAME', None),
        'GS_PROJECT_ID': getattr(settings, 'GS_PROJECT_ID', None),
        'GS_CREDENTIALS_FILE': getattr(settings, 'GS_CREDENTIALS_FILE', None),
        'GS_CREDENTIALS_FILE_EXISTS': False,
        'GOOGLE_APPLICATION_CREDENTIALS': os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'No configurado'),
        'GOOGLE_APPLICATION_CREDENTIALS_EXISTS': False,
        'TEST_CREATE_CLIENT': False,
        'TEST_ACCESS_BUCKET': False,
    }
    
    # Verificar existencia del archivo de credenciales
    if result['GS_CREDENTIALS_FILE'] and os.path.exists(result['GS_CREDENTIALS_FILE']):
        result['GS_CREDENTIALS_FILE_EXISTS'] = True
        
        # Verificar si es JSON válido
        try:
            with open(result['GS_CREDENTIALS_FILE'], 'r') as f:
                json.load(f)
            result['GS_CREDENTIALS_FILE_IS_VALID_JSON'] = True
        except:
            result['GS_CREDENTIALS_FILE_IS_VALID_JSON'] = False
    
    # Verificar variable de entorno
    if result['GOOGLE_APPLICATION_CREDENTIALS'] != 'No configurado':
        result['GOOGLE_APPLICATION_CREDENTIALS_EXISTS'] = os.path.exists(result['GOOGLE_APPLICATION_CREDENTIALS'])
    
    # Probar creación de cliente GCS
    if result['USE_GCS']:
        try:
            from google.cloud import storage
            client = storage.Client(project=result['GS_PROJECT_ID'])
            result['TEST_CREATE_CLIENT'] = True
            
            # Probar acceso al bucket
            try:
                bucket = client.bucket(result['GS_BUCKET_NAME'])
                blobs = list(bucket.list_blobs(max_results=1))
                result['TEST_ACCESS_BUCKET'] = True
                result['BUCKET_CONTAINS_FILES'] = len(blobs) > 0
            except Exception as e:
                result['BUCKET_ERROR'] = str(e)
                
        except Exception as e:
            result['CLIENT_ERROR'] = str(e)
    
    return HttpResponse('<pre>' + json.dumps(result, indent=4) + '</pre>')

# No olvides añadir la URL en urls.py:
# path('check-gcs/', check_gcs_config, name='check_gcs'),
