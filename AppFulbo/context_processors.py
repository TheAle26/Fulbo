# tu_app/context_processors.py
from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leido=False).count()
    else:
        notificaciones_no_leidas = 0
    return {
        'notificaciones_no_leidas': notificaciones_no_leidas,
    }
