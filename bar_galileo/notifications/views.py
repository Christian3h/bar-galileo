from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Notificacion
import json
from itertools import chain

@method_decorator(login_required, name='dispatch')
class NotificacionHistoryView(View):
    """
    Proporciona el historial de notificaciones y el conteo de no leídas.
    """
    def get(self, request):
        # 1. Todas las no leídas
        unread_notifications = Notificacion.objects.filter(usuario=request.user, leida=False)
        
        # 2. Las 2 últimas leídas
        read_notifications = Notificacion.objects.filter(usuario=request.user, leida=True).order_by('-fecha')[:2]

        # 3. Combinar y ordenar
        combined_list = sorted(
            chain(unread_notifications, read_notifications),
            key=lambda instance: instance.fecha,
            reverse=True
        )

        unread_count = unread_notifications.count()
        
        history = [
            {
                "id": n.id,
                "mensaje": n.mensaje,
                "leida": n.leida,
                "fecha": n.fecha.isoformat()
            }
            for n in combined_list
        ]
        
        return JsonResponse({'history': history, 'unread_count': unread_count})

@method_decorator(login_required, name='dispatch')
class MarkAsReadView(View):
    """
    Marca una o todas las notificaciones como leídas.
    """
    def post(self, request):
        data = json.loads(request.body)
        notification_ids = data.get('ids', [])

        if not notification_ids:
            # Marcar todas como leídas
            Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        else:
            # Marcar solo las especificadas
            Notificacion.objects.filter(id__in=notification_ids, usuario=request.user).update(leida=True)
            
        return JsonResponse({'status': 'success'})

