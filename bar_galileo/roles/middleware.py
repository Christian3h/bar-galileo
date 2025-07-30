from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from roles.models import Module, Action, RolePermission

class PermissionMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
        if not hasattr(request.user, 'userprofile') or not request.user.userprofile.rol:
            return None
        modulo = view_func.__module__.split('.')[-2] if '.' in view_func.__module__ else view_func.__module__
        accion = view_func.__name__
        try:
            modulo_obj = Module.objects.get(nombre=modulo)
            accion_obj = Action.objects.get(nombre=accion)
            if not RolePermission.objects.filter(rol=request.user.userprofile.rol, modulo=modulo_obj, accion=accion_obj).exists():
                from django.shortcuts import redirect
                from django.contrib import messages
                messages.warning(request, 'No tienes permiso para acceder a esta sección.')
                return redirect('core:index')
        except Exception:
            pass
        return None
