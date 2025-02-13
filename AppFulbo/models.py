from django.db import models
from django.contrib.auth.models import User  # Modelo de usuario predeterminado de Django
from django.conf import settings
    
class Liga(models.Model):
    nombre_liga= models.CharField(max_length=15,unique=True)
    def __str__(self):
        return self.nombre_liga

class Jugador(models.Model):
    OPCIONES = [
        ('1', 'Arquero'),
        ('2', 'Defensor'),
        ('3', 'Mediocampista'),
        ('4', 'Delantero'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE) 
    apodo = models.CharField(max_length=15)
    posicion = models.CharField(max_length=1, choices=OPCIONES, null=True, blank=True)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE, related_name="jugadores")  # Liga a la que pertenece


    def __str__(self):
        return f"{self.apodo} en liga {self.liga}"

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

# partido = Partido.objects.get(id=1)  # Obtiene un partido específico
# puntajes = partido.puntajes_partidos.all()  # Obtiene todos los puntajes del partido

# # Extraer los valores de puntaje en una lista
# lista_puntajes = [p.puntaje for p in puntajes]
# print(lista_puntajes)  # Ejemplo de salida: [7.5, 8.0, 6.5, 9.0]
