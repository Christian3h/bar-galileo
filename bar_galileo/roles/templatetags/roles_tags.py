from django import template
from roles.models import RolePermission, Module, Action
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@register.filter
def has_perm(user, perm_str):
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'userprofile') or not user.userprofile.rol:
        return False
    try:
        modulo, accion = perm_str.split(',')
        modulo_obj = Module.objects.get(nombre=modulo)
        accion_obj = Action.objects.get(nombre=accion)
        return RolePermission.objects.filter(
            rol=user.userprofile.rol,
            modulo=modulo_obj,
            accion=accion_obj
        ).exists()
    except Exception:
        return False
