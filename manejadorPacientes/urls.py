from django.urls import path
from .views import lista_pacientes, pacientes_view, paciente_view

urlpatterns = [
    # URL para interfaz web (HTML)
    path('pacientes/', lista_pacientes, name='lista_pacientes'),
    
    # URL para API (JSON)
    path('api/pacientes/', pacientes_view, name='pacientes_list'),
    
    # URL para ver/modificar un paciente específico
    path('pacientes/<int:pk>/', paciente_view, name='get_paciente'),
]
