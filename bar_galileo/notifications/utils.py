from .models import Notificacion

# Imports opcionales para Channels: si no están instalados o configurados, hacemos no-op seguro
try:
    from channels.layers import get_channel_layer  # type: ignore
    from asgiref.sync import async_to_sync  # type: ignore
except Exception:  # ModuleNotFoundError, ImportError u otros
    get_channel_layer = None  # type: ignore

    def async_to_sync(func):  # type: ignore
        return func


def notificar_usuario(usuario, mensaje):
    """
    Persiste la notificación en BD y, si Channels está disponible y configurado,
    la envía también por WebSocket al grupo del usuario. Si Channels no está,
    simplemente se omite el envío en tiempo real sin romper el flujo.
    """
    # Guardar en BD (siempre)
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje)

    # Intentar envío por WebSocket solo si Channels está disponible y configurado
    try:
        if get_channel_layer is None:  # Channels no instalado
            print("[INFO] Channels no está instalado; se omite el envío por WebSocket.")
            return

        channel_layer = get_channel_layer()
        if channel_layer is None:  # Channels instalado pero sin CHANNEL_LAYERS configurado
            print("[INFO] CHANNEL_LAYERS no configurado; se omite el envío por WebSocket.")
            return

        print(f"[DEBUG] Enviando notificación a {usuario.username}: {mensaje}")
        async_to_sync(channel_layer.group_send)(
            f"user_{usuario.id}",
            {
                "type": "enviar_mensaje",
                "message": mensaje,
            },
        )
    except Exception as e:
        # Nunca romper el flujo de la app por notificaciones en tiempo real.
        print(f"[WARN] No se pudo enviar notificación por WebSocket: {e}")
