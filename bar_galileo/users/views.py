from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
# Editar información personal

def get_perfil(user):
    from .models import PerfilUsuario
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    return perfil

def editar_info(request):
    perfil = get_perfil(request.user)
    perfil.nombre = request.POST.get('nombre')
    perfil.cedula = request.POST.get('cedula')
    perfil.telefono = request.POST.get('telefono')
    request.user.email = request.POST.get('email')
    perfil.direccion = request.POST.get('direccion')
    perfil.cliente_desde = request.POST.get('cliente_desde')
    perfil.save()
    request.user.save()
    messages.success(request, '¡Información personal actualizada correctamente!')
    return redirect('users:panel_usuario')

# Borrar información personal
@require_POST
def borrar_info(request):
    perfil = get_perfil(request.user)
    perfil.nombre = ''
    perfil.cedula = ''
    perfil.telefono = ''
    request.user.email = ''
    perfil.direccion = ''
    perfil.cliente_desde = ''
    perfil.save()
    request.user.save()
    messages.success(request, '¡Información personal borrada correctamente!')
    return redirect('users:panel_usuario')

# Editar contacto de emergencia
@require_POST
def editar_emergencia(request):
    from .models import Emergencia
    perfil = get_perfil(request.user)
    emergencia, _ = Emergencia.objects.get_or_create(perfil=perfil)
    emergencia.nombre = request.POST.get('emergencia_nombre')
    emergencia.relacion = request.POST.get('emergencia_relacion')
    emergencia.telefono = request.POST.get('emergencia_telefono')
    emergencia.telefono_alt = request.POST.get('emergencia_telefono_alt')
    emergencia.sangre = request.POST.get('emergencia_sangre')
    emergencia.alergias = request.POST.get('emergencia_alergias')
    emergencia.save()
    messages.success(request, '¡Contacto de emergencia actualizado correctamente!')
    return redirect('users:panel_usuario')

# Borrar contacto de emergencia
@require_POST
def borrar_emergencia(request):
    from .models import Emergencia
    perfil = get_perfil(request.user)
    emergencia, _ = Emergencia.objects.get_or_create(perfil=perfil)
    emergencia.nombre = ''
    emergencia.relacion = ''
    emergencia.telefono = ''
    emergencia.telefono_alt = ''
    emergencia.sangre = ''
    emergencia.alergias = ''
    emergencia.save()
    messages.success(request, '¡Contacto de emergencia borrado correctamente!')
    return redirect('users:panel_usuario')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from roles.models import UserProfile, Role
from roles.forms import UserProfileForm
from django.db.models import Case, When, Value, IntegerField

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
        return redirect('users:user_list')
    return render(request, 'users/user_list.html', {'users': users, 'roles': roles})


# Vista para el panel de usuario
from django.contrib.auth.decorators import login_required

@login_required
def panel_usuario(request):
    from .models import PerfilUsuario, Emergencia
    perfil = get_perfil(request.user)
    emergencia, _ = Emergencia.objects.get_or_create(perfil=perfil)
    # Aquí debes construir el dict datos como antes, pero asegurando que emergencia siempre existe
    historial_mensual = {
        'ene': {'mes': 'Enero', 'total': 120000, 'barras': [120000, 80000, 90000, 100000, 110000]},
        'feb': {'mes': 'Febrero', 'total': 160000, 'barras': [160000, 120000, 90000, 180000, 140000]},
        'mar': {'mes': 'Marzo', 'total': 90000, 'barras': [90000, 70000, 60000, 80000, 90000]},
        'abr': {'mes': 'Abril', 'total': 180000, 'barras': [180000, 150000, 120000, 170000, 160000]},
        'may': {'mes': 'Mayo', 'total': 140000, 'barras': [140000, 130000, 120000, 110000, 100000]},
        'jun': {'mes': 'Junio', 'total': 200000, 'barras': [200000, 180000, 170000, 160000, 150000]},
        'jul': {'mes': 'Julio', 'total': 450000, 'barras': [120000, 160000, 90000, 180000, 140000]},
        'ago': {'mes': 'Agosto', 'total': 220000, 'barras': [220000, 210000, 200000, 190000, 180000]},
        'sep': {'mes': 'Septiembre', 'total': 170000, 'barras': [170000, 160000, 150000, 140000, 130000]},
        'oct': {'mes': 'Octubre', 'total': 190000, 'barras': [190000, 180000, 170000, 160000, 150000]},
        'nov': {'mes': 'Noviembre', 'total': 210000, 'barras': [210000, 200000, 190000, 180000, 170000]},
        'dic': {'mes': 'Diciembre', 'total': 250000, 'barras': [250000, 240000, 230000, 220000, 210000]},
    }
    import json
    # Obtener la cuenta actual del usuario (pedidos no facturados)
    from tables.models import Pedido, PedidoItem
    pedidos = Pedido.objects.filter(estado='en_proceso', mesa__isnull=True)
    # Si tienes una relación directa entre usuario y pedido, ajusta el filtro
    items = []
    total = 0
    for pedido in pedidos:
        for item in pedido.items.all():
            items.append({
                'nombre': item.producto.nombre,
                'precio': int(item.subtotal()),
            })
            total += int(item.subtotal())
    datos = {
        'nombre': perfil.nombre,
        'cedula': perfil.cedula,
        'telefono': perfil.telefono,
        'email': request.user.email,
        'direccion': perfil.direccion,
        'cliente_desde': perfil.cliente_desde,
        'cuenta_actual': {
            'total': total,
            'items': items
        },
        'emergencia': {
            'nombre': emergencia.nombre,
            'relacion': emergencia.relacion,
            'telefono': emergencia.telefono,
            'telefono_alt': emergencia.telefono_alt,
            'sangre': emergencia.sangre,
            'alergias': emergencia.alergias,
        },
        'historial_mensual': json.dumps(historial_mensual)
    }
    return render(request, 'users/panel de usuario.html', {'datos': datos})
