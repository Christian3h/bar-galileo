from django.http import HttpResponseForbidden
from functools import wraps
from roles.models import Module, Action, RolePermission
from django.shortcuts import redirect

def permission_required(modulo_nombre, accion_nombre):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated or not hasattr(user, 'userprofile') or not user.userprofile.rol:
                return redirect('core:index')
            try:
                modulo = Module.objects.get(nombre=modulo_nombre)
                accion = Action.objects.get(nombre=accion_nombre)
                if not RolePermission.objects.filter(rol=user.userprofile.rol, modulo=modulo, accion=accion).exists():
                    return redirect('core:index')
            except Exception:
                return redirect('core:index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator