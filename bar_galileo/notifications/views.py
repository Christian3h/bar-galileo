from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Notificacion
import json

@method_decorator(login_required, name='dispatch')
class NotificacionHistoryView(View):
    """
    Proporciona el historial de notificaciones y el conteo de no leídas.
    """
    def get(self, request):
        # Solo notificaciones no leídas
        unread_notifications = Notificacion.objects.filter(
            usuario=request.user, 
            leida=False
        ).order_by('-fecha')

        unread_count = unread_notifications.count()
        
        history = [
            {
                "id": n.id,
                "mensaje": n.mensaje,
                "leida": n.leida,
                "fecha": n.fecha.isoformat()
            }
            for n in unread_notifications
        ]
        
        return JsonResponse({'history': history, 'unread_count': unread_count})

@method_decorator([csrf_exempt, login_required], name='dispatch')
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

@method_decorator(login_required, name='dispatch')
class NotificacionesPendientesView(View):
    def get(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by("-fecha")
        
        data = [{"id": n.id, "mensaje": n.mensaje, "fecha": n.fecha.isoformat()} for n in notificaciones]

        # Marcarlas como leídas
        notificaciones.update(leida=True)

        return JsonResponse(data, safe=False)

