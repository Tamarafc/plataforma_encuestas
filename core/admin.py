from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join
from .models import Encuesta, Pregunta, Opcion, Participacion, Respuesta, HistorialEstado


@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'estado', 'es_publica', 'participantes', 'recientes', 'created_at')
    list_filter = ('estado', 'es_publica')
    search_fields = ('titulo',)
    readonly_fields = ('estado', 'resultados_resumen')
    actions = ['publicar', 'cerrar']

    @admin.display(description='Participantes')
    def participantes(self, obj):
        return obj.total_participantes()

    @admin.display(description='Últimos 7 días')
    def recientes(self, obj):
        return obj.participaciones_recientes()

    @admin.display(description='Resultados')
    def resultados_resumen(self, obj):
        if not obj.pk:
            return '-'
        bloques = []
        for r in obj.resultados():
            filas = format_html_join(
                '', '<li>{}: {} votos ({}%)</li>',
                ((o['opcion'], o['votos'], o['porcentaje']) for o in r['opciones'])
            )
            bloques.append(format_html('<p><b>{}</b> ({} respuestas)</p><ul>{}</ul>',
                                       r['pregunta'], r['total'], filas))
        return format_html_join('', '{}', ((b,) for b in bloques)) or '-'

    def _cambiar(self, request, queryset, nuevo_estado):
        for encuesta in queryset:
            try:
                encuesta.cambiar_estado(nuevo_estado, usuario=request.user)
                self.message_user(request, f"Encuesta '{encuesta.titulo}' cambiada a '{nuevo_estado}'.", messages.SUCCESS)
            except ValidationError as error:
                self.message_user(request, f"'{encuesta.titulo}': {error.messages[0]}", messages.ERROR)

    @admin.action(description='Publicar encuestas seleccionadas')
    def publicar(self, request, queryset):
        self._cambiar(request, queryset, 'publicada')

    @admin.action(description='Cerrar encuestas seleccionadas')
    def cerrar(self, request, queryset):
        self._cambiar(request, queryset, 'cerrada')


admin.site.register(Pregunta)
admin.site.register(Opcion)
admin.site.register(Participacion)
admin.site.register(Respuesta)
admin.site.register(HistorialEstado)