from pathlib import Path
import os
from google.oauth2 import service_account

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-j4yhr0_%5pnhba_+f-#=23tta@t=bb-rgk*g-%t3_d%6mb*i8l'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'manejadorEEGFile',
    'manejadorEventos',
    'manejadorHClinicas',
    'manejadorPacientes',
    'manejadorPruebaDiagnostica',
    'manejadorTipoExamen',
    'social_django'
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyecto.wsgi.application'

# Usar SQLite (comentado, solo para desarrollo local)
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / 'db.sqlite3',
     }
 }

# Configuración de PostgreSQL 
#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.postgresql_psycopg2",
#        "NAME": "project_db",
#        "USER": "project_user",
#        "PASSWORD": "project",
#        "HOST": "34.135.45.48",  # IP externa correcta del servidor de base de datos
#        "PORT": "5432",
#    }
#}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Autenticación con Auth0
LOGIN_URL = "/login/auth0" 
LOGIN_REDIRECT_URL = "/" 
LOGOUT_REDIRECT_URL = "https://dominio_auth0_tenant.auth0.com/v2/logout?returnTo=http%3A%2F%2Fip_publica_instancia:8080" 
SOCIAL_AUTH_TRAILING_SLASH = False # Remove end slash from routes 
SOCIAL_AUTH_AUTH0_DOMAIN = 'dominio_auth0_tenant.auth0.com' 
SOCIAL_AUTH_AUTH0_KEY = 'W8g5KLG4s2ogftLqVDrGwd3xD7JafO0S' 
SOCIAL_AUTH_AUTH0_SECRET = '7MVp47TDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' 
SOCIAL_AUTH_AUTH0_SCOPE = [ 'openid', 'profile','email','role', ] 
AUTHENTICATION_BACKENDS = [ 'monitoring.auth0backend.Auth0', 'django.contrib.auth.backends.ModelBackend', ]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# Configuración de Google Cloud Storage
# Variable para determinar si usamos GCS o almacenamiento local
USE_GCS = True  # Cambiar a False para usar almacenamiento local

if USE_GCS:
    # Configuración básica de Google Cloud Storage
    GS_BUCKET_NAME = 'eeg-files'
    GS_PROJECT_ID = 'proyecto-453621'
    
    # Ruta completa al archivo de credenciales
    GS_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'proyecto-453621-cf370d2140e0.json')
    
    # Comprobar si existe el archivo de credenciales
    if os.path.exists(GS_CREDENTIALS_FILE):
        print(f"Usando credenciales GCS desde: {GS_CREDENTIALS_FILE}")
        
        # No usamos variable de entorno
        # No configuramos DEFAULT_FILE_STORAGE para evitar problemas con django-storages
        
        # Otras configuraciones opcionales
        GS_DEFAULT_ACL = 'publicRead'
        GS_FILE_OVERWRITE = False
    else:
        print(f"ADVERTENCIA: No se encontró el archivo de credenciales en {GS_CREDENTIALS_FILE}")
        USE_GCS = False

# Siempre configuramos almacenamiento local (incluso si usamos GCS)
# Esto es para asegurarnos de que Django pueda manejar archivos localmente si es necesario
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Asegurar que la carpeta existe
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'eeg_files'), exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
