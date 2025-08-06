from .models import Notificacion
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notificar_usuario(usuario, mensaje):
    # Guardar en BD
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje)

    # Enviar por WebSocket
    channel_layer = get_channel_layer()
    print(f"[DEBUG] Enviando notificación a {usuario.username}: {mensaje}")
    async_to_sync(channel_layer.group_send)(
        f"user_{usuario.id}",
        {
            "type": "enviar_mensaje",
            "message": mensaje
        }
    )
