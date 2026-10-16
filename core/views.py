from django.shortcuts import render


def inicio(request):
    return render(request, 'core/inicio.html')


def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)

from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Encuesta, Pregunta, Opcion, Participacion, Respuesta, HistorialEstado
from .serializers import (
    EncuestaSerializer, PreguntaSerializer, OpcionSerializer,
    ParticipacionSerializer, RespuestaSerializer, HistorialEstadoSerializer,
)


def inicio(request):
    return render(request, 'core/inicio.html')


def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)


# Vistas basadas en clase (API REST)
class EncuestaViewSet(viewsets.ModelViewSet):
    queryset = Encuesta.objects.all()
    serializer_class = EncuestaSerializer

    def _cambiar_estado(self, request, nuevo_estado):
        encuesta = self.get_object()
        usuario = request.user if request.user.is_authenticated else None
        try:
            encuesta.cambiar_estado(nuevo_estado, usuario)
        except ValidationError as error:
            return Response({'detail': error.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(encuesta).data)

    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        return self._cambiar_estado(request, 'publicada')

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        return self._cambiar_estado(request, 'cerrada')

    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        encuesta = self.get_object()
        return Response({
            'encuesta': encuesta.titulo,
            'total_participantes': encuesta.total_participantes(),
            'participaciones_ultimos_7_dias': encuesta.participaciones_recientes(),
            'preguntas': encuesta.resultados(),
        })

    @action(detail=False, methods=['get'])
    def mas_activas(self, request):
        return Response(self.get_serializer(Encuesta.mas_activas(), many=True).data)


class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all().order_by('encuesta', 'orden')
    serializer_class = PreguntaSerializer


class OpcionViewSet(viewsets.ModelViewSet):
    queryset = Opcion.objects.all()
    serializer_class = OpcionSerializer


class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer


class RespuestaViewSet(viewsets.ModelViewSet):
    queryset = Respuesta.objects.all()
    serializer_class = RespuestaSerializer


class HistorialEstadoViewSet(viewsets.ModelViewSet):
    queryset = HistorialEstado.objects.all().order_by('-fecha')
    serializer_class = HistorialEstadoSerializer