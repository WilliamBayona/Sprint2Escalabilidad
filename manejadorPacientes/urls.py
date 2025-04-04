from django.urls import path
from .views import lista_pacientes, pacientes_view, paciente_view

urlpatterns = [
    path('pacientes/', lista_pacientes, name='lista_pacientes'),
    path('pacientes/', pacientes_view, name='pacientes_list'),
    path('pacientes/<int:pk>/', paciente_view, name='get_paciente'),
    path('pacientes/<int:pk>/', paciente_view, name='get_paciente'),
]
