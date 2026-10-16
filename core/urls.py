from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('encuestas', views.EncuestaViewSet)
router.register('preguntas', views.PreguntaViewSet)
router.register('opciones', views.OpcionViewSet)
router.register('participaciones', views.ParticipacionViewSet)
router.register('respuestas', views.RespuestaViewSet)
router.register('historial', views.HistorialEstadoViewSet)

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('api/', include(router.urls)),
]