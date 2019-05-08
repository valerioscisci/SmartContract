from django.urls import path
from smartrest import views
from django.contrib.auth import views as auth_views

# Link Generali
urlpatterns = [
    path('StazioneAppaltante/CreaContratto/', views.creacontratto, name='crea_contratto'),  # Url per la creazione di un nuovo contratto
    path('', views.HomePageView.as_view(), name='home'),  #Home
    path('contract_area/', views.ContractAreaView.as_view(), name='contract_area'),  #Contract Area
]

# Login + Cambio Password
urlpatterns += [
    path('login/', auth_views.login, {'template_name': 'registration/login.html'}, name='login'),  #Login
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),  #Logout
    path('password_change/', auth_views.password_change, {'template_name': 'registration/password_change.html'} , name='password_change'),  #Password Change
    path('password-change-done/', auth_views.password_change_done, {'template_name': 'registration/password_change_done.html'}, name='password_change_done'),  #Password Change
]