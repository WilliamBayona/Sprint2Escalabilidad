"""proyecto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # Añade esta línea para la página de inicio
    path('admin/', admin.site.urls),
    path('', include('manejadorEventos.urls')),
    path('', include('manejadorHClinicas.urls')),
    path('', include('manejadorPacientes.urls')),
    path('', include('manejadorPruebaDiagnostica.urls')),
    path('health-check/', views.healthCheck),
    
    # URLs para autenticación
    path('', include('social_django.urls')),  # Asegúrate que esto esté en tus URLpatterns
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG and not getattr(settings, 'USE_GCS', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
