from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
import AppFulbo.forms 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import JugadorForm,LigaForm,MiJugadorForm,PartidoForm
from .models import Liga, Jugador,PuntajePartido,Partido
from django.contrib import messages
from django.db.models import Sum
from datetime import date

def calcular_edad(fecha_nacimiento):
    today = date.today()
    edad = today.year - fecha_nacimiento.year
    # Resta uno si todavía no cumplió años este año
    if (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad

# Create your views here.
def inicio(request):
    return render(request,"AppFulbo/inicio.html") #como tercer argumento le tengo que pasar en forma de diccionario la info


#login y logout
def register(request):
    if request.method == 'POST':
        formulario = AppFulbo.forms.UserRegisterForm(request.POST)

        if formulario.is_valid():
            user = formulario.save()
            authenticated_user = authenticate(username=user.username, password=request.POST['password1'],)

            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('inicio')  # Redirect to the appropriate URL after registration
    else:
        formulario = AppFulbo.forms.UserRegisterForm()

    return render(request, "registro/register.html", {"formulario": formulario})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data = request.POST)

        if form.is_valid():  # Si pasó la validación de Django

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username= username, password=password)

            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                return render(request, "registro/login.html", {"mensaje":"Datos incorrectos"})
           
        else:
            formulario = AuthenticationForm()
            return render(request, "registro/login.html", {"mensaje":"Formulario erroneo","formulario": formulario})

    formulario = AuthenticationForm()

    return render(request, "registro/login.html", {"formulario": formulario})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('inicio')

#editar usuario
@login_required
def edit_profile(request):
    usuario = request.user

    if request.method == 'POST':
        # Usamos el formulario con instance para actualizar el usuario
        miFormulario = AppFulbo.forms.UserEditForm(request.POST, instance=usuario)
        if miFormulario.is_valid():
            # Guardamos los cambios en los datos básicos (email, first_name, last_name)
            usuario = miFormulario.save(commit=False)

            # Si el formulario incluye campos de contraseña y se rellenaron, actualizamos la contraseña
            password1 = miFormulario.cleaned_data.get('password1')
            password2 = miFormulario.cleaned_data.get('password2')
            if password1 and password1 == password2:
                usuario.set_password(password1)

            usuario.save()

            return redirect('inicio')
    else:
        miFormulario = AppFulbo.forms.UserEditForm(instance=usuario)

    return render(request, 'registro/edit_profile.html', {'form': miFormulario})


@login_required
def mis_ligas(request):
    # Obtenemos todos los registros de Jugador asociados al usuario logueado.
    jugadores = Jugador.objects.filter(usuario=request.user)
    # Para cada jugador, obtenemos la liga y le asignamos un atributo 'mi_jugador'
    # que luego se usará en la plantilla.
    ligas_con_jugador = []
    for jugador in jugadores:
        liga = jugador.liga
        liga.mi_jugador = jugador  # Agregamos el jugador a la instancia de liga
        ligas_con_jugador.append(liga)
    
    context = {
        'ligas': ligas_con_jugador
    }
    return render(request, 'AppFulbo/mis_ligas.html', context)



@login_required
def buscar_ligas(request):
    """
    Vista para buscar ligas. Si se ingresa un query, se filtra por nombre (no sensible a mayúsculas).
    Se muestran todas las ligas si no se ingresa nada.
    """
    query = request.GET.get('q', '')
    if query:
        ligas = Liga.objects.filter(nombre_liga__icontains=query)
    else:
        ligas = Liga.objects.all()
    
    context = {
        'ligas': ligas,
        'query': query,
    }
    return render(request, 'AppFulbo/buscar_ligas.html', context)


@login_required
def solicitar_unirse(request, liga_id):
    if request.method == 'POST':
        liga = get_object_or_404(Liga, id=liga_id)
        
        # Verificar si el usuario ya tiene un jugador para esa liga.
        if Jugador.objects.filter(usuario=request.user, liga=liga).exists():
            messages.info(request, f"Ya te has unido a la liga {liga.nombre}.")
            return redirect('mis_ligas')
        
        # Intentar obtener un jugador pre-creado para esa liga (sin usuario asignado).
        jugador = Jugador.objects.filter(liga=liga, usuario__isnull=True).first()
        if jugador:
            jugador.usuario = request.user
            jugador.save()
            messages.success(request, f"Te has unido a la liga {liga.nombre} asignándote el jugador pre-creado.")
        else:
            # Si no hay jugador pre-creado, creamos uno nuevo.
            jugador = Jugador.objects.create(
                usuario=request.user,
                liga=liga,
                # Puedes utilizar datos del usuario o pedir al usuario que complete estos campos
                nombre=request.user.first_name or request.user.username,
                apellido=request.user.last_name or "",
                # Otros campos opcionales, por ejemplo: puntaje=0.0,
            )
            messages.success(request, f"Te has unido a la liga {liga.nombre} creando un nuevo jugador.")
        
        return redirect('mis_ligas')
    else:
        return redirect('buscar_ligas')
    
@login_required
def elegir_o_crear_jugador(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    
    # Verificar si el usuario ya tiene un jugador en esta liga
    if Jugador.objects.filter(usuario=request.user, liga=liga).exists():
        messages.info(request, f"Ya te has unido a la liga {liga.nombre}.")
        return redirect('AppFulbo/mis_ligas')
    
    if request.method == "POST":
        # Si el usuario eligió un jugador existente
        if 'jugador_id' in request.POST:
            jugador_id = request.POST.get('jugador_id')
            jugador = get_object_or_404(Jugador, id=jugador_id, liga=liga, usuario__isnull=True)
            jugador.usuario = request.user
            jugador.save()
            messages.success(request, f"Te has unido a la liga {liga.nombre} asignándote el jugador {jugador.nombre}.")
            return redirect('mis_ligas')
        # Si el usuario decide crear un nuevo jugador
        elif 'crear_nuevo' in request.POST:
            return redirect('AppFulbo/crear_jugador', liga_id=liga.id)
    
    # Si es una solicitud GET, mostrar la lista de jugadores pre-creados disponibles
    jugadores_disponibles = Jugador.objects.filter(liga=liga, usuario__isnull=True)
    context = {
        "liga": liga,
        "jugadores_disponibles": jugadores_disponibles,
    }
    return render(request, "AppFulbo/elegir_jugador.html", context)




@login_required
def partidos_jugados(request):
    # Filtramos todos los registros de PuntajePartido de los jugadores del usuario
    puntajes = PuntajePartido.objects.filter(
        jugador__usuario=request.user
    ).select_related('partido', 'partido__liga', 'jugador').order_by('-partido__fecha_partido')
    
    context = {
        'puntajes': puntajes,
    }
    return render(request, 'AppFulbo/mis_partidos.html', context)

@login_required
def mi_perfil(request):
    user = request.user
    # Se filtran los jugadores del usuario y se anota el puntaje total (suma de puntajes en cada partido)
    jugadores = Jugador.objects.filter(usuario=user).annotate(total_puntaje=Sum('puntajes_partidos__puntaje'))
    
    context = {
        'user': user,
        'jugadores': jugadores,
    }
    return render(request, 'AppFulbo/mi_perfil.html', context)

@login_required
def crear_liga(request):
    if request.method == 'POST':
        form_liga = LigaForm(request.POST)
        form_jugador = JugadorForm(request.POST)  # ya no necesitamos pasar el usuario para filtrar la liga
        if form_liga.is_valid() and form_jugador.is_valid():
            nueva_liga = form_liga.save()
            nuevo_jugador = form_jugador.save(commit=False)
            nuevo_jugador.usuario = request.user
            nuevo_jugador.liga = nueva_liga  # Asigna manualmente la liga recién creada
            nuevo_jugador.save()
            nueva_liga.presidentes.add(request.user)            
            nueva_liga.super_presidentes.add(request.user)
            messages.success(request, "Liga y jugador creados exitosamente.")
            return redirect('ver_liga', liga_id=nueva_liga.id)
    else:
        form_liga = LigaForm()
        form_jugador = JugadorForm()
    return render(request, 'registro/crear_liga.html', {'form_liga': form_liga, 'form_jugador': form_jugador})

def ver_liga(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    mi_jugador = None
    if request.user.is_authenticated:
        mi_jugador = liga.jugadores.filter(usuario=request.user).first()
    context = {
        'liga': liga,
        'mi_jugador': mi_jugador,
    }
    return render(request, 'AppFulbo/ver_liga.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Liga, Jugador, Partido
from .forms import LigaForm  # Formulario para editar nombre/descr, por ejemplo.
# También podrías tener formularios específicos para jugadores, partidos, etc.

def editar_liga(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    # Obtén las relaciones
    presidentes = liga.presidentes.all()
    jugadores = liga.jugadores.all()
    partidos = liga.partidos.all()

    if request.method == "POST":
        action = request.POST.get('action')
        # Acciones posibles:
        if action == "editar_liga":
            form = LigaForm(request.POST, instance=liga)
            if form.is_valid():
                form.save()
                messages.success(request, "Datos de la liga actualizados.")
            else:
                messages.error(request, "Error al actualizar la liga.")
        elif action == "add_president":
            # Supongamos que el formulario trae el username del nuevo presidente.
            nuevo_username = request.POST.get('nuevo_presidente')
            # Aquí deberías buscar al usuario y agregarlo:
            from django.contrib.auth.models import User
            try:
                nuevo_presidente = User.objects.get(username=nuevo_username)
                liga.presidentes.add(nuevo_presidente)
                messages.success(request, f"{nuevo_username} agregado como presidente.")
            except User.DoesNotExist:
                messages.error(request, "El usuario no existe.")
        elif action == "delete_president":
            presidente_id = request.POST.get('presidente_id')
            # Verifica que el usuario sea el super_presidente
            if request.user != liga.super_presidente:
                messages.error(request, "Solo el SuperPresidente puede eliminar a los presidentes.")
            else:
                try:
                    presidente = liga.presidentes.get(id=presidente_id)
                    liga.presidentes.remove(presidente)
                    messages.success(request, "Presidente eliminado.")
                except Exception as e:
                    messages.error(request, "Error al eliminar presidente.")
        elif action == "edit_player":
            # Aquí iría la lógica para editar un jugador
            jugador_id = request.POST.get('jugador_id')
            # Lógica de edición (por ejemplo, abrir formulario en otra vista o modal)
            messages.info(request, f"Editar jugador {jugador_id}.")
        elif action == "delete_player":
            jugador_id = request.POST.get('jugador_id')
            try:
                jugador = Jugador.objects.get(id=jugador_id)
                jugador.delete()
                messages.success(request, "Jugador eliminado.")
            except Exception as e:
                messages.error(request, "Error al eliminar jugador.")
        elif action == "edit_match":
            # Lógica para editar partido
            partido_id = request.POST.get('partido_id')
            messages.info(request, f"Editar partido {partido_id}.")
        elif action == "delete_match":
            partido_id = request.POST.get('partido_id')
            try:
                partido = Partido.objects.get(id=partido_id)
                partido.delete()
                messages.success(request, "Partido eliminado.")
            except Exception as e:
                messages.error(request, "Error al eliminar partido.")

        # Después de la acción, redirige a la misma vista para refrescar la información.
        return redirect('editar_liga', liga_id=liga.id)

    else:
        # Para editar datos de la liga, inicializamos un formulario:
        form = LigaForm(instance=liga)

    context = {
        'liga': liga,
        'form': form,
        'presidentes': presidentes,
        'jugadores': jugadores,
        'partidos': partidos,
    }
    return render(request, 'AppFulbo/editar_liga.html', context)


@login_required
def crear_jugador(request, liga_id):
    league = get_object_or_404(Liga, id=liga_id)
    if request.method == 'POST':
        form = JugadorForm(request.POST, liga=league)
        if form.is_valid():
            nuevo_jugador = form.save(commit=False)
            nuevo_jugador.liga = league  # Asigna la liga manualmente.
            # Si fuera necesario asignar usuario, se podría hacer aquí, p.ej.:
            # nuevo_jugador.usuario = request.user
            nuevo_jugador.save()
            messages.success(request, "Jugador creado exitosamente.")
            return redirect('ver_liga', liga_id=league.id)
    else:
        form = JugadorForm(liga=league)
    return render(request, 'registro/crear_jugador.html', {'form': form, 'liga': league})

@login_required
def crear_partido(request, liga_id):
    # Obtenemos la liga a la que se creará el partido
    league = get_object_or_404(Liga, id=liga_id)
    
    if request.method == 'POST':
        form = PartidoForm(request.POST, league=league)
        if form.is_valid():
            # Creamos el objeto Partido sin guardar aún, para asignar la liga.
            partido = form.save(commit=False)
            partido.liga = league
            partido.save()
            
            # Obtenemos la lista de jugadores que participaron.
            jugadores_seleccionados = form.cleaned_data.get('jugadores')
            
            # Para cada jugador seleccionado, creamos un registro de participación (por ejemplo, PuntajePartido)
            # Aquí se asume que puntaje se inicializa en 0.0.
            for jugador in jugadores_seleccionados:
                PuntajePartido.objects.create(
                    jugador=jugador,
                    partido=partido,
                    puntaje=0.0
                )
            
            messages.success(request, "Partido creado exitosamente.")
            return redirect('ver_liga', liga_id=league.id)
    else:
        form = PartidoForm(league=league)
    
    return render(request, 'registro/crear_partido.html', {'form': form, 'liga': league})

def ver_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    # Obtenemos los puntajes de este partido, incluyendo la información del jugador
    puntajes = partido.puntajes_partidos.select_related('jugador').all()
    context = {
        'partido': partido,
        'puntajes': puntajes,
    }
    return render(request, 'AppFulbo/ver_partido.html', context)