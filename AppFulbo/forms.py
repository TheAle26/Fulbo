from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Jugador, Liga,Partido,Mensaje,Notificacion
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
        # No incluimos el campo 'liga' porque se asignará manualmente en la vista.
        fields = ['apodo', 'posicion','numero']
        labels = {
            'apodo': 'Apodo',
            'posicion': 'Posición',
            'numero': 'Camiseta'
        }

    def __init__(self, *args, **kwargs):
        # Se espera recibir la instancia de la liga como argumento para filtrar el apodo.
        self.liga = kwargs.pop('liga', None)
        super().__init__(*args, **kwargs)

    def clean_apodo(self):
        apodo = self.cleaned_data.get('apodo')
        if self.liga:
            # Excluir el jugador actual de la validación si es que existe (al editar)
            qs = Jugador.objects.filter(apodo__iexact=apodo, liga=self.liga)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este apodo ya existe en esta liga. Por favor, elige otro.")
        return apodo

    
    help_texts = {
            'apodo': 'Ingrese un apodo único en la liga.'
        }
    error_messages = {
            'apodo': {
                'unique': "Ya existe este apodo en esta liga.",
            },
        }


class LigaForm(forms.ModelForm):
    class Meta:
        model = Liga
        fields = ['nombre_liga','descripcion']
        labels = {
            'nombre_liga': 'Nombre de la liga',
            'descripcion': 'Descripccion de la liga'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }
        help_texts = {
            'nombre_liga': 'Ingrese un nombre único para la liga.'
        }
        error_messages = {
            'nombre_liga': {
                'unique': "Ya existe una liga con este nombre. Por favor, elige otro nombre.",
            },
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields.pop('nombre_liga', None)

        

class MiJugadorForm(JugadorForm):
    class Meta(JugadorForm.Meta):
        # Por ejemplo, podrías agregar o modificar campos, si fuera necesario.
        pass


    def __init__(self, *args, **kwargs):
        # Se espera recibir el usuario logueado para filtrar las ligas
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Obtener los IDs de las ligas en las que el usuario ya tiene un jugador.
            user_league_ids = Jugador.objects.filter(usuario=user).values_list('liga', flat=True)
           # Filtrar el queryset del campo liga para excluir esas ligas.
            self.fields['liga'].queryset = Liga.objects.exclude(id__in=user_league_ids)




class PartidoForm(forms.ModelForm):
    # Campo adicional para seleccionar los jugadores de la liga que participaron.
    jugadores = forms.ModelMultipleChoiceField(
        queryset=None,  # Lo definiremos en __init__
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Jugadores que participaron"
    )
    
    class Meta:
        model = Partido
        fields = ['fecha_partido', 'cancha']
        labels = {
            'fecha_partido': 'Fecha del partido',
            'cancha': 'Cancha',
        }
        widgets = {
            'fecha_partido': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Esperamos recibir la instancia de la liga (league) para filtrar los jugadores.
        league = kwargs.pop('league', None)
        super().__init__(*args, **kwargs)
        if league:
            # El queryset del campo 'jugadores' se limita a los jugadores de esa liga.
            self.fields['jugadores'].queryset = league.jugadores.all()

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['remitente', 'contenido']
        widgets = {
            'remitente': forms.Select(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
