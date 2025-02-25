from django.db import models
from django.contrib.auth.models import User  # Modelo de usuario predeterminado de Django
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

NUMERO_CHOICES = [(i, str(i)) for i in range(1, 100)]
    
class Liga(models.Model):
    nombre_liga = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    presidentes = models.ManyToManyField(User, related_name="ligas_presididas",null=True)  # Relación ManyToMany con los presidentes
    super_presidente = models.ForeignKey(
         settings.AUTH_USER_MODEL,
         on_delete=models.SET_NULL,
         null=True,
         blank=True,
         related_name="ligas_super_presididas",
         help_text="El super presidente de la liga, con privilegios especiales."
     )    
    def __str__(self):
        return self.nombre_liga

class Jugador(models.Model):
    OPCIONES = [
        ('1', 'Arquero'),
        ('2', 'Defensor'),
        ('3', 'Mediocampista'),
        ('4', 'Delantero'),
    ]
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    apodo = models.CharField(max_length=15)
    posicion = models.CharField(max_length=1, choices=OPCIONES, null=True, blank=True)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name="jugadores")
    numero = models.IntegerField(
        choices=NUMERO_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        null=True,
        blank=True,
        help_text="Seleccione un número entre 1 y 99."
    )
    activo = models.BooleanField(default=True, help_text="Indica si el jugador está activo en la liga.")

    def __str__(self):
        return f"{self.apodo} en liga {self.liga}"

    class Meta:
        unique_together = ('apodo', 'liga')
        # O, en Django 2.2+:
        # constraints = [
        #     models.UniqueConstraint(fields=['apodo', 'liga'], name='unique_apodo_per_liga')
        # ]
 


class Partido(models.Model):
    fecha_partido = models.DateField(null=True, blank=True)
    cancha = models.CharField(max_length=15)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name="partidos")  # Liga a la que pertenece
    
    def __str__(self):
        return f"Partido del {self.fecha_partido} en {self.cancha}"

class PuntajePartido(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="puntajes_partidos")
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name="puntajes_partidos")
    puntaje = models.FloatField(default=0.0)  # Puntaje del jugador en este partido

    def __str__(self):
        return f"{self.jugador} - {self.partido}: {self.puntaje}"


class Conversacion(models.Model):
    usuario1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='conversaciones_iniciadas',
        on_delete=models.CASCADE
    )
    usuario2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='conversaciones_recibidas',
        on_delete=models.CASCADE
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversación: {self.usuario1.username} - {self.usuario2.username}"

    class Meta:
        unique_together = ('usuario1', 'usuario2')

class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion,
        related_name='mensajes',
        on_delete=models.CASCADE
    )
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mensajes_enviados',
        on_delete=models.CASCADE
    )
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.remitente.username} - {self.fecha_envio:%d/%m/%Y %H:%M}"

    
class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('MSG', 'Mensaje'),
        ('SOL', 'Solicitud'),
        # Podés agregar otros tipos según necesites
    ]
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notificaciones",
        on_delete=models.CASCADE
    )
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    mensaje = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)  # Para enlazar a la acción relacionada
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario} - {self.mensaje}"

