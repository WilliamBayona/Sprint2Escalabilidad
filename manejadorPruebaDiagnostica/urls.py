from django.urls import path
from .views import (
    lista_pruebas_diagnosticas, 
    pruebas_diagnosticas_view, 
    prueba_diagnostica_view, 
    subir_eeg_view,
    upload_eeg,
    visualizar_eeg_view
)

urlpatterns = [
    path('pruebas/', pruebas_diagnosticas_view),
    path('prueba/<int:pk>/', prueba_diagnostica_view),
    path('prueba/<int:pk>/subir_eeg/', subir_eeg_view),
    path('prueba/<int:prueba_id>/subir_eeg/', upload_eeg, name='upload_eeg'),
    path('prueba-diagnostica/<int:pk>/visualizar-eeg/', visualizar_eeg_view, name='visualizar_eeg'),
    
]