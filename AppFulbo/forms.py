from django import forms 

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Jugador


# class Restaurante_form(forms.Form):
#     nombre = forms.CharField(max_length=99)
#     calificacion = forms.FloatField(min_value=0,max_value=5) #quiero que sea el promedio de las reseñas hechas
#     descripcion = forms.CharField(max_length=250)
#     ubicacion=forms.CharField(max_length=99)
#     instagram = forms.URLField()
#     foto=forms.ImageField()
    
#     def clean_foto(self):
#         foto = self.cleaned_data.get('foto')
#         if foto:
#             # Aquí puedes agregar validaciones adicionales para la imagen si es necesario
#             pass
#         return foto

# class Reseña_form(forms.Form):
#     restaurante = forms.ModelChoiceField(queryset=Restaurante.objects.all(), empty_label=None, to_field_name="nombre", widget=forms.Select(attrs={'class': 'form-control'})) #quiero que sea una lista despegable de los que ya existen
#     puntuacion = forms.FloatField(min_value=0,max_value=5) 
#     #ubicacion = forms.CharField(max_length=250)
#     fecha_de_visita=forms.DateField()
#     reseña=forms.CharField(max_length=150)
#     foto=forms.ImageField()

#     def clean_foto(self):
#         foto = self.cleaned_data.get('foto')
#         if foto:
#             # Aquí puedes agregar validaciones adicionales para la imagen si es necesario
#             pass
#         return foto


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label="Nombre de usuario")  # Cambié 'usuario' a 'username'
    # email = forms.EmailField(label="Correo electrónico")
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")

    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)
    fecha_nacimiento = forms.DateField(required=False)
    widgets = {
        'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'last_name', 'first_name','fecha_nacimiento']
        help_texts = {k: "" for k in fields}



# Clase 24, agregamos el UserEditForm
class UserEditForm(forms.ModelForm):
    email = forms.EmailField(label='Correo electrónico')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput)
    last_name = forms.CharField(label='Apellido')
    first_name = forms.CharField(label='Nombre')

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'last_name', 'first_name']
        help_texts = {k: "" for k in fields}



class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['usuario', 'nombre', 'apellido', 'posicion_favorita', 'liga']
