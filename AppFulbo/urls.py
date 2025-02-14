from django.urls import path
from AppFulbo import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('inicio/',views.inicio,name='inicio'),
    path('login/',views.login_request,name='login'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),
    path('register/',views.register,name='register'),
    path('edit_Profile/', views.edit_profile, name='edit_Profile'),
    path('mi_perfil/', views.mi_perfil, name='mi_perfil'),
    
    path('ligas/buscar/', views.buscar_ligas, name='buscar_ligas'),
    path('ligas/unirse/<int:liga_id>/', views.solicitar_unirse, name='solicitar_unirse'),
    path('mis_ligas/',views.mis_ligas, name='mis_ligas'),
    path('jugador/crear/<int:liga_id>/', views.crear_jugador, name='crear_jugador'),
    path('ligas/crear/', views.crear_liga, name='crear_liga'),
    path('ligas/<int:liga_id>/', views.ver_liga, name='ver_liga'),
    path('mis_partidos/', views.partidos_jugados, name='mis_partidos'),
]
