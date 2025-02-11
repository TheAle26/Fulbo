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
]
