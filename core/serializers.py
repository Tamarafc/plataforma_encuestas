from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from.models import Encuesta, Pregunta, Opcion, Participacion, Respuesta, HistorialEstado


class ReglasDeNegocioSerializer(serializers.ModelSerializer):
    """Ejecuta el clean() del modelo, para reutilizar las reglas de negocio en la API."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instancia = self.Meta.model(**attrs)
        try:
            instancia.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
        return attrs


class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = ['id', 'pregunta', 'texto']


class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = ['id', 'encuesta', 'texto', 'tipo', 'orden', 'obligatoria', 'opciones']


class EncuestaSerializer(serializers.ModelSerializer):
    total_participantes = serializers.SerializerMethodField()

    def get_total_participantes(self, obj):
        return obj.total_participantes()

    class Meta:
        model = Encuesta
        fields = ['id', 'titulo', 'descripcion', 'creador', 'es_publica', 'estado',
                  'fecha_inicio', 'fecha_fin', 'total_participantes', 'created_at']
        read_only_fields = ['estado', 'created_at']


class ParticipacionSerializer(ReglasDeNegocioSerializer):
    class Meta:
        model = Participacion
        fields = ['id', 'encuesta', 'participante', 'fecha']
        read_only_fields = ['fecha']


class RespuestaSerializer(ReglasDeNegocioSerializer):
    class Meta:
        model = Respuesta
        fields = ['id', 'participacion', 'pregunta', 'opcion', 'texto_respuesta', 'created_at']
        read_only_fields = ['created_at']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstado
        fields = ['id', 'encuesta', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'fecha']