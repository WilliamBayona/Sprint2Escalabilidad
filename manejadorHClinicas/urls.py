from django.urls import path, include
from .views import lista_historias_clinicas, historias_clinicas_view, historia_clinica_view


urlpatterns = [
    path('historias_clinicas/', lista_historias_clinicas, name='lista_historias_clinicas'),
    path('historias_clinicas/', historias_clinicas_view, name='historias_clinicas_list'),
    path('historias_clinicas/<int:pk>/', historia_clinica_view, name='get_historia_clinicas'),
    path(r'', include('django.contrib.auth.urls')),
    path(r'', include('social_django.urls'))
]
