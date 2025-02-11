from django.urls import path
from AppFulbo import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('inicio/',views.inicio,name='inicio'),
    path('login/',views.login_request,name='iniciar_sesion'),
    path('register/',views.register,name='register'),
    path('Iniciar Sesion/',views.login_request,name='Iniciar Sesion'),
    path('logout/', LogoutView.as_view(template_name='registro/logout.html'), name='logout'),
    path('edit_Profile/', views.edit_Profile, name='edit_Profile'),
    path('user/',views.mi_usuario, name="user"),
    
    path('ligas/buscar/', views.buscar_ligas, name='buscar_ligas'),
    path('ligas/unirse/<int:liga_id>/', views.solicitar_unirse, name='solicitar_unirse'),
    path('ligas/unirse/<int:liga_id>/', views.elegir_o_crear_jugador, name='elegir_o_crear_jugador'),
    # Asumiendo que ya tengas definida la vista mis_ligas y crear_jugador:
    path('mis_ligas/',views.mis_ligas, name='mis_ligas'),
    path('jugador/crear/<int:liga_id>/', views.crear_jugador, name='crear_jugador'),
    path('mis_partidos/',views.mis_ligas, name='mis_partidos'),
]
