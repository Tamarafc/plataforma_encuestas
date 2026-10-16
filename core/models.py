from django.db import models
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import timedelta
from django.db.models import Count

class Encuesta(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('publicada', 'Publicada'),
        ('cerrada', 'Cerrada'),
    ]
    TRANSICIONES = {
            'borrador': ['publicada'],
            'publicada': ['cerrada'],
            'cerrada': [],
        }
    
    def cambiar_estado(self, nuevo_estado, usuario=None):
            """Cambia el estado validando las reglas y deja registro en el historial."""
            if nuevo_estado not in self.TRANSICIONES.get(self.estado, []):
                raise ValidationError(
                    f"No se puede pasar de '{self.estado}' a '{nuevo_estado}'."
                )
    
            if nuevo_estado == 'publicada':
                if not self.preguntas.exists():
                    raise ValidationError("La encuesta necesita al menos una pregunta para publicarse.")
                for pregunta in self.preguntas.filter(tipo='opcion'):
                    if pregunta.opciones.count() < 2:
                        raise ValidationError(
                            f"La pregunta '{pregunta.texto}' necesita al menos 2 opciones."
                        )
    
            with transaction.atomic():
                anterior = self.estado
                self.estado = nuevo_estado
                self.save()
                HistorialEstado.objects.create(
                    encuesta=self,
                    estado_anterior=anterior,
                    estado_nuevo=nuevo_estado,
                    cambiado_por=usuario,
                )
    def total_participantes(self):
        return self.participaciones.count()

    def participaciones_recientes(self, dias=7):
        desde = timezone.now() - timedelta(days=dias)
        return self.participaciones.filter(fecha__gte=desde).count()

    def resultados(self):
        """Para cada pregunta de opción única: votos y porcentaje por opción."""
        resultado = []
        for pregunta in self.preguntas.filter(tipo='opcion'):
            total = pregunta.respuesta_set.count()
            opciones = []
            for opcion in pregunta.opciones.annotate(votos=Count('respuesta')):
                porcentaje = round(opcion.votos * 100 / total, 1) if total else 0
                opciones.append({
                    'opcion': opcion.texto,
                    'votos': opcion.votos,
                    'porcentaje': porcentaje,
                })
            resultado.append({'pregunta': pregunta.texto, 'total': total, 'opciones': opciones})
        return resultado

    @classmethod
    def mas_activas(cls, limite=5):
        return cls.objects.annotate(n=Count('participaciones')).order_by('-n')[:limite]
    
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='encuestas')
    es_publica = models.BooleanField(default=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='borrador')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo
       

class Pregunta(models.Model):
    TIPOS = [
        ('opcion', 'Opción única'),
        ('texto', 'Texto libre'),
    ]
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPOS, default='opcion')
    orden = models.PositiveIntegerField(default=1)
    obligatoria = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.texto


class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pregunta.texto[:30]} - {self.texto}"

class Participacion(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='participaciones')
    participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participaciones')
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('encuesta', 'participante')  # una participación por persona
    def __str__(self):
        return f"{self.participante} en {self.encuesta}"
    def clean(self):
        if not self._state.adding or not self.encuesta_id:
            return
        ahora = timezone.now()
        if self.encuesta.estado != 'publicada':
            raise ValidationError("Solo se puede participar en encuestas publicadas.")
        if self.encuesta.fecha_inicio and ahora < self.encuesta.fecha_inicio:
            raise ValidationError("La encuesta todavía no ha comenzado.")
        if self.encuesta.fecha_fin and ahora > self.encuesta.fecha_fin:
            raise ValidationError("La encuesta ya terminó.")

class Respuesta(models.Model):
    participacion = models.ForeignKey(Participacion, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(Opcion, on_delete=models.SET_NULL, null=True, blank=True)
    texto_respuesta = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ('participacion', 'pregunta')
    def clean(self):
        if not self.participacion_id or not self.pregunta_id:
            return
        if self.pregunta.encuesta_id != self.participacion.encuesta_id:
            raise ValidationError("La pregunta no pertenece a la encuesta de esta participación.")
        if self.pregunta.tipo == 'opcion':
            if not self.opcion_id:
                raise ValidationError("Debes elegir una opción para esta pregunta.")
            if self.opcion.pregunta_id != self.pregunta_id:
                raise ValidationError("La opción elegida no pertenece a esa pregunta.")
        elif self.pregunta.obligatoria and not self.texto_respuesta.strip():
            raise ValidationError("Esta pregunta es obligatoria, escribe una respuesta.")

class HistorialEstado(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=10)
    estado_nuevo = models.CharField(max_length=10)
    cambiado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(default=timezone.now)
