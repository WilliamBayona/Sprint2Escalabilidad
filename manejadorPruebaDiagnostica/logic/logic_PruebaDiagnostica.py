import tempfile
import os
import uuid
import datetime
import traceback
import logging
import json
import mne
from ..models import PruebaDiagnostica
from manejadorPruebaDiagnostica.models import EEGFile
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from google.oauth2 import service_account

# Configurar logging
logger = logging.getLogger(__name__)

# Verificar si estamos en entorno local o producción
USAR_GOOGLE_CLOUD = getattr(settings, 'USAR_GOOGLE_CLOUD', False)

def get_pruebas_diagnosticas():
    return PruebaDiagnostica.objects.all()

def get_prueba_diagnostica(pk):
    return PruebaDiagnostica.objects.get(id=pk)

def crear_prueba_diagnostica(data):
    return PruebaDiagnostica.objects.create(**data)

def actualizar_prueba_diagnostica(pk, data):
    prueba = get_prueba_diagnostica(pk)
    for key, value in data.items():
        setattr(prueba, key, value)
    prueba.save()
    return prueba

def subir_archivo_eeg(prueba_id, archivo):
    """
    Sube un archivo EDF y extrae metadatos usando MNE.
    Utiliza explícitamente las credenciales sin depender de variables de entorno.
    """
    prueba = get_prueba_diagnostica(prueba_id)

    if prueba.tipo_de_prueba != 'EEG':
        return None, "Solo las pruebas EEG pueden tener archivos EDF."

    temp_file_path = None
    
    try:
        # Guardar archivo temporalmente para procesarlo con MNE
        with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as temp_file:
            if hasattr(archivo, 'seek') and callable(archivo.seek):
                archivo.seek(0)
            
            temp_file.write(archivo.read())
            temp_file_path = temp_file.name
            print(f"Archivo temporal guardado en: {temp_file_path}")

        try:
            # Cargar archivo con MNE para extraer metadatos
            raw = mne.io.read_raw_edf(temp_file_path, preload=True)
            
            # Generar nombre único para el archivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_id = uuid.uuid4().hex[:8]
            unique_filename = f"eeg_files/eeg_{prueba_id}_{timestamp}_{file_id}.edf"
            
            # Crear instancia de EEGFile
            eeg_file = EEGFile()
            
            # Determinar si usamos GCS según la configuración
            use_gcs = getattr(settings, 'USE_GCS', False)
            
            if use_gcs:
                print("Usando Google Cloud Storage para almacenar el archivo")
                
                try:
                    from google.cloud import storage
                    
                    # Cargar credenciales directamente desde el archivo
                    credentials_file = os.path.join(settings.BASE_DIR, 'proyecto-453621-cf370d2140e0.json')
                    
                    if not os.path.exists(credentials_file):
                        print(f"ADVERTENCIA: No se encontró el archivo de credenciales en {credentials_file}")
                        return None, f"El archivo de credenciales no existe: {credentials_file}"
                    
                    # Crear credenciales de manera explícita
                    credentials = service_account.Credentials.from_service_account_file(credentials_file)
                    
                    # Crear cliente de Google Cloud Storage con las credenciales explícitas
                    client = storage.Client(
                        project=settings.GS_PROJECT_ID,
                        credentials=credentials
                    )
                    
                    # Obtener referencia al bucket
                    bucket = client.bucket(settings.GS_BUCKET_NAME)
                    
                    # Crear blob y subir archivo
                    blob = bucket.blob(unique_filename)
                    
                    with open(temp_file_path, 'rb') as f:
                        blob.upload_from_file(f)
                    
                    print(f"Archivo subido exitosamente a GCS: {unique_filename}")
                    
                    # Generar URL pública
                    gcs_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{unique_filename}"
                    
                    # Guardar datos en el modelo
                    eeg_file.file = unique_filename
                    eeg_file.gcs_url = gcs_url
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error detallado al subir a GCS: {error_details}")
                    return None, f"Error al subir a Google Cloud Storage: {str(e)}"
            else:
                # Almacenamiento local
                archivo.seek(0)
                file_path = default_storage.save(unique_filename, ContentFile(archivo.read()))
                eeg_file.file = file_path
                print(f"Archivo guardado localmente como: {file_path}")
            
            # Guardar metadatos del EEG
            eeg_file.recording_date = raw.info.get('meas_date')
            eeg_file.num_signals = len(raw.ch_names)
            eeg_file.duration = raw.times[-1] if raw.times.size > 0 else None
            eeg_file.channel_names = raw.ch_names
            eeg_file.sampling_rates = {ch: raw.info['sfreq'] for ch in raw.ch_names}
            
            # Guardar el modelo
            eeg_file.save()
            
            # Asociar archivo a la prueba
            prueba.eeg_file = eeg_file
            prueba.save()
            
            print(f"Archivo EEG asociado correctamente a la prueba {prueba_id}")
            return eeg_file, None
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error procesando archivo EEG: {error_details}")
            return None, f"Error procesando el archivo EDF: {str(e)}"
            
        finally:
            # Eliminar el archivo temporal si existe
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("Archivo temporal eliminado")
                
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error inesperado: {error_details}")
        return None, f"Error inesperado: {str(e)}"
