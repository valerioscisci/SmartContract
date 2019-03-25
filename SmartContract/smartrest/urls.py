from django.urls import path
from smartrest import views

urlpatterns = [
    path('StazioneAppaltante/CreaContratto/', views.creacontratto, name='crea_contratto'),  # Url per la creazione di un nuovo contratto
]