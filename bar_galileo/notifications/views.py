from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Notificacion

@method_decorator(login_required, name='dispatch')
class NotificacionesPendientesView(View):
    def get(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by("-fecha")
        
        data = [{"id": n.id, "mensaje": n.mensaje, "fecha": n.fecha.isoformat()} for n in notificaciones]

        # Marcarlas como leídas
        notificaciones.update(leida=True)

        return JsonResponse(data, safe=False)

