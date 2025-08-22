from django.contrib import messages
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
from roles.models import UserProfile, Role
from roles.forms import UserProfileForm

from .models_historial import HistorialMensual
from notifications.utils import notificar_usuario
from .models import PerfilUsuario, Emergencia

# Editar información personal
def get_perfil(user):
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    return perfil

def editar_info(request):
    perfil = get_perfil(request.user)
    errors = {}
    nombre = request.POST.get('nombre', perfil.nombre)
    cedula = request.POST.get('cedula', perfil.cedula)
    telefono = request.POST.get('telefono', perfil.telefono)
    direccion = request.POST.get('direccion', perfil.direccion)
    cliente_desde = request.POST.get('cliente_desde', perfil.cliente_desde)
    email = request.POST.get('email', request.user.email)
    # Validaciones avanzadas
    if not nombre:
        errors['nombre'] = 'El nombre es obligatorio.'
    if not cedula or not cedula.isdigit():
        errors['cedula'] = 'La cédula es obligatoria y debe ser numérica.'
    if not telefono or not telefono.isdigit() or len(telefono) < 10:
        errors['telefono'] = 'El teléfono es obligatorio, debe ser numérico y tener al menos 10 dígitos.'
    if not email or '@' not in email:
        errors['email'] = 'El email debe ser un correo válido.'
    # Si hay errores, renderizar el panel con los errores
    if errors:
        datos = {
            # ...otros datos del panel...
            'nombre': nombre,
            'cedula': cedula,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'cliente_desde': cliente_desde,
            'info_errors': errors,
        }
        return render(request, 'users/panel de usuario.html', {'datos': datos})
    # Si no hay errores, guardar y redirigir
    perfil.nombre = nombre
    perfil.cedula = cedula
    # Agregar +57 automáticamente si no está
    if telefono and not telefono.startswith('+57'):
        telefono = '+57' + telefono
    perfil.telefono = telefono
    perfil.direccion = direccion
    perfil.cliente_desde = cliente_desde
    perfil.save()
    request.user.email = email
    request.user.save()
    messages.success(request, '¡Información personal actualizada correctamente!')
    return redirect('users:panel_usuario')

# Borrar información personal
@require_POST
def borrar_info(request):
    perfil = get_perfil(request.user)
    from .models import Emergencia
    emergencia = Emergencia.objects.filter(perfil=perfil).first()
    # Limpiar datos del perfil
    perfil.nombre = ''
    perfil.cedula = ''
    perfil.telefono = ''
    perfil.direccion = ''
    perfil.cliente_desde = ''
    perfil.save()
    # Limpiar datos de emergencia si existe
    if emergencia:
        emergencia.nombre = ''
        emergencia.relacion = ''
        emergencia.telefono = ''
        emergencia.telefono_alt = ''
        emergencia.sangre = ''
        emergencia.alergias = ''
        emergencia.save()
    # Limpiar email del usuario
    request.user.email = ''
    request.user.save()
    messages.success(request, '¡Información personal y contacto de emergencia borrados correctamente!')
    return redirect('users:panel_usuario')

# Editar contacto de emergencia
@require_POST
def editar_emergencia(request):
    perfil = get_perfil(request.user)
    from .models import Emergencia
    emergencia, _ = Emergencia.objects.get_or_create(perfil=perfil)
    errors = {}
    nombre = request.POST.get('emergencia_nombre', emergencia.nombre)
    relacion = request.POST.get('emergencia_relacion', emergencia.relacion)
    telefono = request.POST.get('emergencia_telefono', emergencia.telefono)
    telefono_alt = request.POST.get('emergencia_telefono_alt', emergencia.telefono_alt)
    sangre = request.POST.get('emergencia_sangre', emergencia.sangre)
    alergias = request.POST.get('emergencia_alergias', emergencia.alergias)
    # Validaciones avanzadas
    if not nombre:
        errors['nombre'] = 'El nombre es obligatorio.'
    if not telefono or not telefono.isdigit():
        errors['telefono'] = 'El teléfono es obligatorio y debe ser numérico.'
    if telefono_alt and not telefono_alt.isdigit():
        errors['telefono_alt'] = 'El teléfono alternativo debe ser numérico.'
    # Si hay errores, renderizar el panel con los errores
    if errors:
        emergencia.nombre = nombre
        emergencia.relacion = relacion
        emergencia.telefono = telefono
        emergencia.telefono_alt = telefono_alt
        emergencia.sangre = sangre
        emergencia.alergias = alergias
        datos = {
            # ...otros datos del panel...
            'emergencia': {
                'nombre': nombre,
                'relacion': relacion,
                'telefono': telefono,
                'telefono_alt': telefono_alt,
                'sangre': sangre,
                'alergias': alergias,
            },
            'emergencia_errors': errors
        }
        return render(request, 'users/panel de usuario.html', {'datos': datos})
    # Si no hay errores, guardar y redirigir
    emergencia.nombre = nombre
    emergencia.relacion = relacion
    emergencia.telefono = telefono
    emergencia.telefono_alt = telefono_alt
    emergencia.sangre = sangre
    emergencia.alergias = alergias
    emergencia.save()
    messages.success(request, '¡Contacto de emergencia actualizado correctamente!')
    return redirect('users:panel_usuario')

# Borrar contacto de emergencia
@require_POST
def borrar_emergencia(request):
    import logging
    logger = logging.getLogger('django')
    perfil = get_perfil(request.user)
    emergencia = Emergencia.objects.filter(perfil=perfil).first()
    if emergencia:
        emergencia.nombre = ''
        emergencia.relacion = ''
        emergencia.telefono = ''
        emergencia.telefono_alt = ''
        emergencia.sangre = ''
        emergencia.alergias = ''
        emergencia.save()
        logger.warning(f"Emergencia borrada para perfil {perfil.id}: {emergencia.__dict__}")
        messages.success(request, '¡Contacto de emergencia borrado correctamente!')
    else:
        logger.warning(f"No se encontró emergencia para perfil {perfil.id}")
    return redirect('users:panel_usuario')

def user_list(request):
    users = User.objects.all().select_related('userprofile')
    # Ordenar: usuarios con rol al final
    users = users.annotate(
        is_user_role=Case(
            When(userprofile__rol__nombre='usuario', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_user_role', 'username')
    roles = Role.objects.all()
    if request.method == 'POST':
        pass
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})

# Vista para el panel de usuario
@login_required
def panel_usuario(request):
    perfil = get_perfil(request.user)
    emergencia = Emergencia.objects.filter(perfil=perfil).first()
    # Obtener historial mensual desde la base de datos
    historial_objs = HistorialMensual.objects.filter(perfil=perfil)
    historial_mensual = {}
    for obj in historial_objs:
        historial_mensual[obj.mes] = {
            'mes': obj.mes,
            'total': obj.total,
            'barras': obj.barras or []
        }
    # Si no hay datos, todos los meses estarán vacíos
    datos = {
        'nombre': perfil.nombre,
        'cedula': perfil.cedula,
        'telefono': perfil.telefono,
        'email': request.user.email,
        'direccion': perfil.direccion,
        'cliente_desde': perfil.cliente_desde,
        'emergencia': {
            'nombre': emergencia.nombre if emergencia else '',
            'relacion': emergencia.relacion if emergencia else '',
            'telefono': emergencia.telefono if emergencia else '',
            'telefono_alt': emergencia.telefono_alt if emergencia else '',
            'sangre': emergencia.sangre if emergencia else '',
            'alergias': emergencia.alergias if emergencia else '',
        },
        'historial_mensual': historial_mensual
    }
    return render(request, 'users/panel de usuario.html', {'datos': datos})
from notifications.utils import notificar_usuario

def user_list(request):
    users = User.objects.all().select_related('userprofile')
    # Ordenar: usuarios con rol al final
    users = users.annotate(
        is_user_role=Case(
            When(userprofile__rol__nombre='usuario', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_user_role', 'username')
    roles = Role.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        rol_id = request.POST.get('rol_id')
        user = User.objects.get(id=user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.rol_id = rol_id
        profile.save()
        
        rol = Role.objects.get(id=rol_id)
        mensaje = f"El rol del usuario '{user.username}' ha sido actualizado a '{rol.name}'."
        notificar_usuario(request.user, mensaje)

        return redirect('users:user_list')
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})




