from django.urls import path
from .views import lista_eventos, eventos_view, evento_view

urlpatterns = [
    path('eventos/', lista_eventos, name='lista_eventos'),
    path('eventos/', eventos_view, name='eventos_list'),
    path('eventos/<int:pk>/', evento_view, name='get_evento'),
]
