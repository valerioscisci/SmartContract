from django.urls import path
from smartrest import views
from django.contrib.auth import views as auth_views


# Link Generali
urlpatterns = [
    path('contract_area/set_contratti/', views.setcontratti, name='set_contratti'), # Url per il settaggio iniziale dei contratti
    path('', views.HomePageView.as_view(), name='home'),  # Home
    path('transazioni/', views.visualizzatransazioni, name='visualizza_transazioni'),  # Visualizza lista transazioni
    path('contract_area/', views.ContractAreaView.as_view(), name='contract_area'),  # Contract Area
]

# Login + Cambio Password + registrazione
urlpatterns += [
    path('login/', auth_views.login, {'template_name': 'registration/login.html'}, name='login'),  # Login
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),  # Logout
    path('password_change/', auth_views.password_change, {'template_name': 'registration/password_change.html'} , name='password_change'),  # Password Change
    path('password-change-done/', auth_views.password_change_done, {'template_name': 'registration/password_change_done.html'}, name='password_change_done'),  # Password Change
    path('registrazione/', views.registrazione,  name='registra'), # Registrazione
]

# Contract Area
urlpatterns += [
    path('contract_area/nuovo_contratto/', views.nuovocontratto, name='nuovo_contratto'), # Contract Area - Nuovo Contratto
    path('contract_area/nuovo_contratto_redirect/', views.nuovocontrattoredirect.as_view(), name='nuovo_contratto_redirect'), # Contract Area - Nuovo Contratto Redirect
    path('contract_area/nuova_misura/', views.nuovamisura, name='nuova_misura'), # Contract Area - Nuova Misura
    path('contract_area/nuova_misura_redirect/', views.nuovamisuraredirect.as_view(), name='nuova_misura_redirect'),  # Contract Area - Nuova Misura Redirect
    path('contract_area/libretto_misure/', views.librettomisure, name='libretto_misure'),  #Contract Area - Libretto Misure
    path('contract_area/registro_contabilita/', views.registrocont, name='registro_cont'), # Contract Area - Registro Contabilità
    path('contract_area/registro_contabilita/', views.registrocontredirect.as_view(), name='registro_cont_redirect'), # Contract Area - Registro Contabilità Redirect
    path('contract_area/stato_avanzamento/', views.statoavanzamento, name='stato_avanzamento'),  #Contract Area - Stato Avanzamento Lavori
    path('contract_area/nuova_voce_giornale/', views.nuovavocegiornale, name='nuova_voce_giornale'),  # Contract Area - Nuova Voce Giornale
    path('contract_area/nuova_voce_giornale_redirect/', views.nuovavocegiornaleredirect.as_view(), name='nuova_voce_giornale_redirect'), # Contract Area - Nuova Voce Giornale Redirect
    path('contract_area/giornale_lavori/', views.giornalelavori, name='giornale_lavori'),  #Contract Area - Giornale dei Lavori
]
