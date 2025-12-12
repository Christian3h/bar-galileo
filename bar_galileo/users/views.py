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
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from tables.models import Pedido

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
    email = request.POST.get('email', request.user.email)
    if not nombre:
        errors['nombre'] = 'El nombre es obligatorio.'
    if not cedula or not cedula.isdigit():
        errors['cedula'] = 'La cédula es obligatoria y debe ser numérica.'
    if not telefono or not telefono.isdigit() or len(telefono) < 10:
        errors['telefono'] = 'El teléfono es obligatorio, debe ser numérico y tener al menos 10 dígitos.'
    if not email or '@' not in email:
        errors['email'] = 'El email debe ser un correo válido.'
    if errors:
        datos = {
            'nombre': nombre,
            'cedula': cedula,
            'telefono': telefono,
            'email': email,
            'direccion': direccion,
            'info_errors': errors,
        }
        return render(request, 'users/panel de usuario.html', {'datos': datos})
    perfil.nombre = nombre
    perfil.cedula = cedula
    if telefono and not telefono.startswith('+57'):
        telefono = '+57' + telefono
    perfil.telefono = telefono
    perfil.direccion = direccion
    perfil.save()
    request.user.email = email
    request.user.save()
    notificar_usuario(request.user, '¡Información personal actualizada correctamente!')
    return redirect('users:panel_usuario')

@require_POST
def borrar_info(request):
    perfil = get_perfil(request.user)
    emergencia = Emergencia.objects.filter(perfil=perfil).first()
    perfil.nombre = ''
    perfil.cedula = ''
    perfil.telefono = ''
    perfil.direccion = ''
    perfil.save()
    if emergencia:
        emergencia.nombre = ''
        emergencia.relacion = ''
        emergencia.telefono = ''
        emergencia.telefono_alt = ''
        emergencia.sangre = ''
        emergencia.alergias = ''
        emergencia.save()
    request.user.email = ''
    request.user.save()
    notificar_usuario(request.user, '¡Información personal y contacto de emergencia borrados correctamente!')
    return redirect('users:panel_usuario')

@require_POST
def editar_emergencia(request):
    perfil = get_perfil(request.user)
    emergencia, _ = Emergencia.objects.get_or_create(perfil=perfil)
    errors = {}
    nombre = request.POST.get('emergencia_nombre', emergencia.nombre)
    relacion = request.POST.get('emergencia_relacion', emergencia.relacion)
    telefono = request.POST.get('emergencia_telefono', emergencia.telefono)
    telefono_alt = request.POST.get('emergencia_telefono_alt', emergencia.telefono_alt)
    sangre = request.POST.get('emergencia_sangre', emergencia.sangre)
    alergias = request.POST.get('emergencia_alergias', emergencia.alergias)
    if not nombre:
        errors['nombre'] = 'El nombre es obligatorio.'
    if not telefono or not telefono.isdigit():
        errors['telefono'] = 'El teléfono es obligatorio y debe ser numérico.'
    if telefono_alt and not telefono_alt.isdigit():
        errors['telefono_alt'] = 'El teléfono alternativo debe ser numérico.'
    if errors:
        emergencia.nombre = nombre
        emergencia.relacion = relacion
        emergencia.telefono = telefono
        emergencia.telefono_alt = telefono_alt
        emergencia.sangre = sangre
        emergencia.alergias = alergias
        datos = {
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
    emergencia.nombre = nombre
    emergencia.relacion = relacion
    emergencia.telefono = telefono
    emergencia.telefono_alt = telefono_alt
    emergencia.sangre = sangre
    emergencia.alergias = alergias
    emergencia.save()
    notificar_usuario(request.user, '¡Contacto de emergencia actualizado correctamente!')
    return redirect('users:panel_usuario')

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
        notificar_usuario(request.user, '¡Contacto de emergencia borrado correctamente!')
    else:
        logger.warning(f"No se encontró emergencia para perfil {perfil.id}")
    return redirect('users:panel_usuario')

@login_required
def panel_usuario(request):
    perfil = get_perfil(request.user)

    if request.method == 'POST':
        if 'delete_avatar' in request.POST:
            if perfil.avatar:
                perfil.avatar.delete(save=True)
                notificar_usuario(request.user, '¡Foto de perfil eliminada!')
            return redirect('users:panel_usuario')

        if 'avatar' in request.FILES:
            try:
                img = Image.open(request.FILES['avatar'])

                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=85)
                buffer.seek(0)

                file_name = f"{request.user.id}_avatar.webp"
                perfil.avatar.save(file_name, ContentFile(buffer.read()), save=True)
                notificar_usuario(request.user, '¡Foto de perfil actualizada!')

            except Exception as e:
                notificar_usuario(request.user, f"Error al procesar la imagen: {e}")

            return redirect('users:panel_usuario')

    emergencia = Emergencia.objects.filter(perfil=perfil).first()
    historial_objs = HistorialMensual.objects.filter(perfil=perfil)
    historial_mensual = {}
    for obj in historial_objs:
        historial_mensual[obj.mes] = {
            'mes': obj.mes,
            'total': obj.total,
            'barras': obj.barras or []
        }

    pedidos_facturados = Pedido.objects.filter(
        usuarios=request.user,
        estado='facturado'
    ).select_related('mesa', 'factura').order_by('-fecha_actualizacion')

    # Obtener la cuenta actual (pedido en proceso)
    pedido_actual = Pedido.objects.filter(
        usuarios=request.user,
        estado='en_proceso'
    ).select_related('mesa').prefetch_related('items__producto').first()

    cuenta_actual_data = {
        'total': 0,
        'items': []
    }
    if pedido_actual:
        cuenta_actual_data['total'] = pedido_actual.total()
        cuenta_actual_data['items'] = [{
            'nombre': item.producto.nombre,
            'precio': item.subtotal()
        } for item in pedido_actual.items.all()]

    datos = {
        'nombre': perfil.nombre,
        'cedula': perfil.cedula,
        'telefono': perfil.telefono,
        'email': request.user.email,
        'direccion': perfil.direccion,
        'avatar_url': perfil.avatar.url if perfil.avatar else None,
        'emergencia': {
            'nombre': emergencia.nombre if emergencia else '',
            'relacion': emergencia.relacion if emergencia else '',
            'telefono': emergencia.telefono if emergencia else '',
            'telefono_alt': emergencia.telefono_alt if emergencia else '',
            'sangre': emergencia.sangre if emergencia else '',
            'alergias': emergencia.alergias if emergencia else '',
        },
        'historial_mensual': historial_mensual,
        'pedidos_facturados': pedidos_facturados,
        'cuenta_actual': cuenta_actual_data
    }
    return render(request, 'users/panel de usuario.html', {'datos': datos})

@login_required
def user_list(request):
    users = User.objects.all().select_related('userprofile')
    users = users.annotate(
        is_user_role=Case(
            When(userprofile__rol__nombre='usuario', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('is_user_role', 'username')
    roles = Role.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action', 'change_role')
        
        if action == 'change_role':
            user_id = request.POST.get('user_id')
            rol_id = request.POST.get('rol_id')
            user = User.objects.get(id=user_id)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.rol_id = rol_id
            profile.save()

            rol = Role.objects.get(id=rol_id)
            mensaje = f"El rol del usuario '{user.username}' ha sido actualizado a '{rol.nombre}'."

            # Solo notificar si el usuario está autenticado
            if request.user.is_authenticated:
                notificar_usuario(request.user, mensaje)

            return redirect('users:user_list')
    
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})

from django.http import JsonResponse

def user_list_api(request):
    users = User.objects.all().order_by('username')
    data = [{'id': user.id, 'username': user.username, 'nombre': user.get_full_name() or user.username} for user in users]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def cambiar_password(request):
    """Vista para que el administrador cambie la contraseña de cualquier usuario"""
    from .models import CambioPasswordAuditoria
    
    try:
        # Obtener datos del formulario
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        motivo = request.POST.get('motivo', '')
        
        # Validaciones
        if not user_id or not new_password or not confirm_password:
            notificar_usuario(request.user, 'Error: Todos los campos obligatorios deben ser completados.')
            return redirect('users:user_list')
        
        if new_password != confirm_password:
            notificar_usuario(request.user, 'Error: Las contraseñas no coinciden.')
            return redirect('users:user_list')
        
        if len(new_password) < 8:
            notificar_usuario(request.user, 'Error: La contraseña debe tener al menos 8 caracteres.')
            return redirect('users:user_list')
        
        # Obtener el usuario a modificar
        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            notificar_usuario(request.user, 'Error: Usuario no encontrado.')
            return redirect('users:user_list')
        
        # No permitir cambiar la contraseña del superusuario por seguridad
        if usuario.is_superuser and not request.user.is_superuser:
            notificar_usuario(request.user, 'Error: No tiene permisos para cambiar la contraseña de un superusuario.')
            return redirect('users:user_list')
        
        # Cambiar la contraseña
        usuario.set_password(new_password)
        usuario.save()
        
        # Obtener la IP del administrador
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Registrar en auditoría
        CambioPasswordAuditoria.objects.create(
            usuario_modificado=usuario,
            administrador=request.user,
            ip_address=ip_address,
            motivo=motivo
        )
        
        # Notificar éxito
        notificar_usuario(request.user, f'La contraseña de "{usuario.username}" ha sido cambiada exitosamente. Este cambio ha sido registrado en el sistema de auditoría.')
        
    except Exception as e:
        notificar_usuario(request.user, f'Error al cambiar la contraseña: {str(e)}')
    
    return redirect('users:user_list')


@login_required
def historial_password(request):
    """Vista para ver el historial de cambios de contraseña"""
    from .models import CambioPasswordAuditoria
    from django.core.paginator import Paginator
    
    # Obtener todos los cambios ordenados por fecha descendente
    cambios = CambioPasswordAuditoria.objects.all().select_related(
        'usuario_modificado', 'administrador'
    ).order_by('-fecha_cambio')
    
    # Paginación
    paginator = Paginator(cambios, 25)  # 25 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/historial_password.html', {
        'page_obj': page_obj,
        'total_cambios': cambios.count()
    })