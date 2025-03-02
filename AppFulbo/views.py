from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest,HttpResponseForbidden,JsonResponse
import datetime
import AppFulbo.forms 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout,get_user_model
from django.contrib.auth.decorators import login_required
from .forms import JugadorForm,LigaForm,MiJugadorForm,PartidoForm,MensajeForm
from .models import Liga, Jugador,PuntajePartido,Partido,Mensaje, Notificacion,Conversacion, SolicitudUnionLiga
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone



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
    if request.method == 'POST':
        liga_id = request.POST.get('liga_id')
        #ligas = Liga.objects.all()
        #liga_elegida = ligas.get(id=liga_id)
        liga_elegida = get_object_or_404(Liga, id=liga_id)
        #aca creo la solicitud
        mi_jugador = liga_elegida.jugadores.filter(usuario=request.user).first()
        if mi_jugador:
            messages.success(request, f"Ya estas en esta liga.")
        else:
            
            if not SolicitudUnionLiga.objects.filter(usuario=request.user, liga=liga_elegida).exists():
                SolicitudUnionLiga.objects.create(usuario=request.user, liga=liga_elegida)
                messages.success(request, "Solicitud enviada.")
            else:
                messages.info(request, "Ya has solicitado unirte a esta liga.")
        return redirect('ver_liga', liga_id=liga_elegida.id)
    else:
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
            nueva_liga.super_presidente = request.user
            nueva_liga.save()

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

def editar_liga(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    # Obtén las relaciones
    presidentes = liga.presidentes.all()
    jugadores = liga.jugadores.filter(activo=True)
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
            presidente_id = request.POST.get('presidente_id')
            # Verifica que el usuario sea el super_presidente
            if request.user != liga.super_presidente:
                messages.error(request, "Solo el SuperPresidente puede eliminar a los presidentes.")
            else:
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
            jugador_id = request.POST.get('jugador_id')
            return redirect('editar_jugador', jugador_id=jugador_id)
        
        elif action == "abandonar_liga":
            # Verifica si el usuario es el super_presidente
            if request.user == liga.super_presidente:
                messages.error(request, "Debes asignar a un superpresidente antes de irte.")
            else:
                # Elimina al usuario de la lista de presidentes
                liga.presidentes.remove(request.user)
                # Buscar el jugador asociado al usuario en esta liga y marcarlo como inactivo.
                jugador = liga.jugadores.filter(usuario=request.user, activo=True).first()
                if jugador:
                    jugador.activo = False
                    jugador.save()
                messages.success(request, "Has abandonado la liga y tu jugador ha sido desactivado.")
                return redirect('ver_liga', liga_id=liga.id)
            
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
        
        elif action == "hacer_super_presidente":
            # Verificar que el usuario que realiza la acción sea el superpresidente actual
            if request.user != liga.super_presidente:
                messages.error(request, "Solo el superpresidente actual puede realizar este cambio.")
            else:
                nuevo_super_id = request.POST.get('presidente_id')
                try:
                    nuevo_super = liga.presidentes.get(id=nuevo_super_id)
                except liga.presidentes.model.DoesNotExist:
                    nuevo_super = None

                if not nuevo_super:
                    messages.error(request, "El presidente elegido no existe o no es válido.")
                else:
                    # Verificamos que el usuario elegido ya sea presidente
                    if nuevo_super not in liga.presidentes.all():
                        messages.error(request, "El usuario elegido debe ser presidente antes de ser designado como superpresidente.")
                    else:
                        # Asignamos el nuevo superpresidente y guardamos
                        liga.super_presidente = nuevo_super
                        liga.save()
                        messages.success(request, f"{nuevo_super.username} ahora es el superpresidente de la liga.")
            return redirect('editar_liga', liga_id=liga.id)


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

def mensaje_automatico_solicitud_liga(request, user, solicitud,mensaje):
    destinatario = solicitud.usuario
    conversacion = Conversacion.objects.filter(
        Q(usuario1=user, usuario2=destinatario) |
        Q(usuario1=destinatario, usuario2=user)
    ).first()

    if not conversacion:
        if user.id < destinatario.id:
            conversacion = Conversacion.objects.create(usuario1=user, usuario2=destinatario)
        else:
            conversacion = Conversacion.objects.create(usuario1=destinatario, usuario2=user)

    Mensaje.objects.create(
        conversacion=conversacion,
        remitente=user,
        contenido=mensaje
    )

@login_required
def asociar_jugador(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUnionLiga, id=solicitud_id)
    liga = solicitud.liga

    if request.user in liga.presidentes.all():
        jugadores = liga.jugadores.filter(usuario__isnull=True)
        if request.method == "POST":
            action = request.POST.get('action')
            if action == "asociar_a_jugador":
                jugador_id = request.POST.get('jugador_id')
                jugador = get_object_or_404(Jugador, id=jugador_id, liga=liga)
                jugador.usuario = solicitud.usuario
                jugador.save()
                solicitud.delete()
                mensaje = f"Te acepte en la liga {liga}."
                mensaje_automatico_solicitud_liga(request, request.user, solicitud,mensaje)
                solicitud.delete()  # Se rechaza la solicitud eliminándola
                messages.success(request, "Has sido asociado a la liga y al jugador seleccionado.")
                return redirect('ver_liga', liga_id=liga.id)
            else:
                messages.error(request, "Opción no válida.")
                return redirect('asociar_jugador', solicitud_id=solicitud.id)
        else:

            context = {
                'solicitud': solicitud,
                'liga': liga,
                'jugadores': jugadores
            }
            return render(request, 'AppFulbo/agregar_a_liga.html', context)
    


@login_required
def gestionar_solicitudes(request, liga_id):
    liga = get_object_or_404(Liga, id=liga_id)
    if request.user in liga.presidentes.all():
        if request.method == "POST":
            action = request.POST.get('action')
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(SolicitudUnionLiga, id=solicitud_id, liga=liga)
            
            if action == "aceptar":
                return redirect('asociar_jugador', solicitud_id=solicitud.id)
            
            elif action == "rechazar":
                mensaje = f"He rechazado tu solicitud a la la liga {liga}."
                mensaje_automatico_solicitud_liga(request, request.user, solicitud,mensaje)
                solicitud.delete()  # Se rechaza la solicitud eliminándola
                messages.success(request, "Solicitud rechazada.")
            else:
                messages.error(request, "Opción no válida.")
            
            return redirect('gestionar_solicitudes', liga_id=liga.id)
        
        else:
            solicitudes = liga.solicitudes_union.all()
            return render(request, 'AppFulbo/gestionar_solicitudes.html', {'solicitudes': solicitudes, 'liga': liga})

        
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


def editar_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    
    # Verificar si el usuario es presidente de la liga a la que pertenece el jugador.
    if request.user not in jugador.liga.presidentes.all():
        return HttpResponseForbidden("No tenés permisos para editar este jugador.")

    if request.method == 'POST':
        form = JugadorForm(request.POST, instance=jugador, liga=jugador.liga)
        if form.is_valid():
            form.save()
            messages.success(request, "Jugador actualizado correctamente.")
            # Redirige a la vista de edición de la liga.
            return redirect('editar_liga', liga_id=jugador.liga.id)
    else:
        form = JugadorForm(instance=jugador, liga=jugador.liga)
    
    context = {
        'form': form,
        'jugador': jugador
    }
    return render(request, 'AppFulbo/editar_jugador.html', context)


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

@login_required
def inbox(request):
    conversaciones = Conversacion.objects.filter(
        Q(usuario1=request.user) | Q(usuario2=request.user)
    ).order_by('-fecha_actualizacion')
    return render(request, 'mensajes/inbox.html', {'conversaciones': conversaciones})

@login_required
def conversacion_detail(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    # Verificar que el usuario sea participante de la conversación
    if request.user not in [conversacion.usuario1, conversacion.usuario2]:
        return HttpResponseForbidden("No tenés acceso a esta conversación.")
    mensajes = conversacion.mensajes.all().order_by('fecha_envio')

    if request.method == "POST":
        contenido = request.POST.get('contenido')
        if contenido:
            Mensaje.objects.create(
                conversacion=conversacion,
                remitente=request.user,
                contenido=contenido
            )
            return redirect('conversacion_detail', conversacion_id=conversacion.id)
    return render(request, 'mensajes/conversacion_detail.html', {
        'conversacion': conversacion,
        'mensajes': mensajes
    })
    


def obtener_mensajes(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    mensajes = conversacion.mensajes.all().order_by('fecha_envio')
    
    mensajes_data = []
    for mensaje in mensajes:
        mensajes_data.append({
            'id': mensaje.id,
            'remitente': mensaje.remitente.username,
            'contenido': mensaje.contenido,
            'fecha_envio': mensaje.fecha_envio.strftime("%d/%m/%Y %H:%M")
        })
    return JsonResponse({'mensajes': mensajes_data})


User = get_user_model()
@login_required
def nuevo_chat(request):
    # Listamos usuarios que no sean el actual (para iniciar un chat)
    usuarios = User.objects.exclude(id=request.user.id)
    if request.method == "POST":
        destinatario_id = request.POST.get('destinatario')
        if destinatario_id:
            destinatario = get_object_or_404(User, id=destinatario_id)
            # Buscar conversación existente sin importar el orden.
            conversacion = Conversacion.objects.filter(
                Q(usuario1=request.user, usuario2=destinatario) |
                Q(usuario1=destinatario, usuario2=request.user)
            ).first()
            if not conversacion:
                # Para evitar duplicados, definí un orden, por ejemplo:
                if request.user.id < destinatario.id:
                    conversacion = Conversacion.objects.create(usuario1=request.user, usuario2=destinatario)
                else:
                    conversacion = Conversacion.objects.create(usuario1=destinatario, usuario2=request.user)
            return redirect('conversacion_detail', conversacion_id=conversacion.id)
    return render(request, 'mensajes/nuevo_chat.html', {'usuarios': usuarios})

@login_required
def marcar_todas_notificaciones_ajax(request):
    if request.method == "POST":
        request.user.notificaciones.filter(leido=False).update(leido=True)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def enviar_mensaje_ajax(request, conversacion_id):
    if request.method == 'POST':
        conversacion = get_object_or_404(Conversacion, id=conversacion_id)
        contenido = request.POST.get('mensaje', '').strip()
        if not contenido:
            return JsonResponse({'error': 'El mensaje no puede estar vacío.'}, status=400)
        
        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            contenido=contenido,
            fecha_envio=timezone.now()
        )
        
        # Actualizamos la fecha de actualización de la conversación
        conversacion.fecha_actualizacion = timezone.now()
        conversacion.save()
        
        return JsonResponse({
            'success': True,
            'mensaje_id': mensaje.id,
            'remitente': mensaje.remitente.username,
            'contenido': mensaje.contenido,
            'fecha_envio': mensaje.fecha_envio.strftime("%d/%m/%Y %H:%M")
        })
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)