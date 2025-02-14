from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Jugador, Liga
from django.contrib.auth import get_user_model


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
    username = forms.CharField(label="Nombre de usuario")
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)
    # fecha_nacimiento = forms.DateField(
    #     required=False,
    #     widget=forms.DateInput(attrs={'type': 'date'})
    # )
    
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            # 'fecha_nacimiento'
        ]
        help_texts = {k: "" for k in fields}




User = get_user_model()

class UserEditForm(forms.ModelForm):
    # Los campos de contraseña son opcionales para no forzar su cambio
    password1 = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Repetir Nueva Contraseña', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = [ 'first_name', 'last_name','email']
        help_texts = {k: "" for k in fields}

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        # Si se ingresó alguna contraseña, ambas deben coincidir
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user



class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['usuario', 'apodo', 'posicion', 'liga']


class LigaForm(forms.ModelForm):
    class Meta:
        model = Liga
        fields = ['nombre_liga']
        labels = {
            'nombre_liga': 'Nombre de la Liga'
        }
        help_texts = {
            'nombre_liga': 'Ingrese un nombre único para la liga.'
        }
        error_messages = {
            'nombre_liga': {
                'unique': "Ya existe una liga con este nombre. Por favor, elige otro nombre.",
            },
        }
        

class MiJugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        # Excluimos el campo 'liga' para que no se muestre en el formulario
        fields = ['apodo', 'posicion']
        labels = {
            'apodo': 'Apodo',
            'posicion': 'Posición',
        }

    # def __init__(self, *args, **kwargs):
    #     # Se espera recibir el usuario logueado para filtrar las ligas
    #     user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)
    #     if user:
    #         # Obtener los IDs de las ligas en las que el usuario ya tiene un jugador.
    #         user_league_ids = Jugador.objects.filter(usuario=user).values_list('liga', flat=True)
    #         # Filtrar el queryset del campo liga para excluir esas ligas.
    #         self.fields['liga'].queryset = Liga.objects.exclude(id__in=user_league_ids)
